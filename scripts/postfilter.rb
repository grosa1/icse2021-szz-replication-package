require 'json'
require 'set'
require 'time'
require 'code-assertions'

EMULATE        = false
RESULTS_FOLDER = ARGV[0]
REPOS_FOLDER   = ARGV[1]
SUFFIX         = ".issue-filter.json"

if EMULATE
    puts "This is emulation mode. If the repository can not be found, RANDOM commit dates will be generated. Please, remove this for the real run. Do you want to continue? (y/N)"
    result = STDIN.gets.chomp
    if result.downcase != 'y'
        puts "Bye."
        exit 0
    end
end

unless RESULTS_FOLDER || REPOS_FOLDER
    warn "Please specify the JSON input folder and the repos folder"

    exit -1
end

class EmulatedRepository
    def initialize(local)
        @local = local
        warn "Emulating non-existing repository #{local}"
    end

    def date(commit)
        from = Time.at(0)
        to = Time.now
        return Time.at(from + rand * (to.to_f - from.to_f))
    end
end

class Repository
    def self.get(local)
        if EMULATE && !FileTest.exist?(local)
            return EmulatedRepository.new(local)
        else
            return Repository.new(local)
        end
    end

    def initialize(local)
        @local = local
        assert("Local repository #{local} must exist") { FileTest.exist?(local) }
    end

    def date(commit)
        result = nil

        Dir.chdir(@local) do
            result = `git show -s --format=%ci "#{commit}"`
        end

        result.assert_nn!
        return Time.parse(result)
    end
end

Dir.glob(File.join(RESULTS_FOLDER, "*.json")).select { |e| !e.end_with?(SUFFIX) }.each do |filename|
    data = JSON.parse(File.read(filename))

    to_skip = false
    data.each do |json|
        repo_folder = File.join(REPOS_FOLDER, json['repo_name'])

        earliest_issue_date      = json['earliest_issue_date']
        best_scenario_issue_date = json['best_scenario_issue_date']

        assert("The json in #{filename} contains both the earliest issue date and the best_scenario_issue_date") { !(earliest_issue_date && best_scenario_issue_date) }
        if !earliest_issue_date && !best_scenario_issue_date
            to_skip = true
            break
        end

        issue_date  = Time.parse((earliest_issue_date || best_scenario_issue_date) + " UTC")
        issue_date.assert_nn!

        repository = Repository.get(repo_folder)

        json['inducing_commit_hash'] = [] unless json['inducing_commit_hash']
        json['inducing_commit_hash'].select! { |commit| repository.date(commit) < issue_date }

        warn ("The oracle is after the issue date! #{JSON.generate(json)}") unless json['bug_commit_hash'].all? { |commit| repository.date(commit) < issue_date }
    end

    if to_skip
        warn "Skipping #{filename} because some data point contained no issue date."
        next
    end

    File.open(filename.sub(".json", SUFFIX), 'w') do |f|
        f.write JSON.generate(data)
    end
end

puts "Performing a sanity-check of the results..."
Dir.glob(File.join(RESULTS_FOLDER, "*.json")).select { |e| !e.end_with?(SUFFIX) }.each do |json_normal_filename|
    json_filtered_filename = json_normal_filename.sub(".json", SUFFIX)

    unless FileTest.exist?(json_filtered_filename)
        warn "Filtered issue file #{json_filtered_filename} does not exist."
        next
    end

    json_normal     = JSON.parse(File.read(json_normal_filename))
    json_filtered   = JSON.parse(File.read(json_filtered_filename))

    assert("The two JSONs must have exactly the same size! #{json_normal_filename}") { json_normal.size == json_filtered.size }
    for i in 0...json_normal.size
        json_normal_part    = json_normal[i]
        json_filtered_part  = json_filtered[i]

        json_normal_part.each do |key, value|
            if key != 'inducing_commit_hash'
                assert("The filtered version cannot differ on fields other than BIC (diff #{key}, #{json_normal_part['id']}, #{json_normal_filename})") { value == json_filtered_part[key] }
            else
                assert("The filtered version cannot contain additional BICs (diff #{key}, #{json_normal_part['id']}, #{json_normal_filename})") { Set.new(value) >= Set.new(json_filtered_part[key]) }
            end
        end
    end
end
puts "No issues found."
puts "This was generated with the EMULATE mode on!" if EMULATE
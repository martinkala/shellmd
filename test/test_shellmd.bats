load bats-assert/load.bash
load bats-support/load.bash

SHELLMD_PATH=./

@test "Run unit tests" {
	run python3 ${SHELLMD_PATH}/test/unit/parseTest.py
	assert_success
}

@test "Print help message" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --help
	assert_success
}

@test "Run simple happy cases in README.MD" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README.md
	assert_success
}

@test "Run negative scenario - broken code block" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README_broken_cb.md
	assert_failure
}

@test "Run MD without code block - no failure expected" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README_no_cb.md
	assert_success
}

@test "Run MD with validations in comments" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=test/README_no_cb.md
	assert_success
}

@test "run md without comments with overiding --all-executable" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README_no_comments.md --all-executable=yes
	assert_success
}

@test "run md validations" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README_validations.md 
	assert_success
}

@test "run md with specific variable file" {
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README_config_file.md --config-file=test/config_file_01
	assert_success
}

@test "run md without output file to store output" {
    OUTPUT_FILE=/tmp/shellmd_output_file.txt
    rm -rf ${OUTPUT_FILE}

	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README.md
    assert_success
	run ls -la ${OUTPUT_FILE}
    assert_failure
}

@test "run md with output file to store output" {
    OUTPUT_FILE=/tmp/shellmd_output_file.txt
    rm -rf ${OUTPUT_FILE}

	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README.md --output-file=${OUTPUT_FILE}
	assert_success

	run ls -la ${OUTPUT_FILE}
	assert_success

	run cat ${OUTPUT_FILE}
	assert_output --partial "stdout:"

	run rm ${OUTPUT_FILE}
	assert_success
}

@test "run md with output file to store output and debug-env-vars stored in output file" {
    export VVAARR1=first
    export VVAARR2=second
    OUTPUT_FILE=/tmp/shellmd_output_file.txt
	run python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README.md --output-file=${OUTPUT_FILE} --debug-env-vars=VVAARR1,VVAARR2
	assert_success

    # check file exist
	run ls -la ${OUTPUT_FILE}
	assert_success

    # check outpfile contains variable VVAARR1
	run cat ${OUTPUT_FILE}
	assert_output --partial "VVAARR1=first"

    # check outpfile contains variable VVAARR1
    run cat ${OUTPUT_FILE}
    assert_output --partial "VVAARR2=second"

    # clean file after test
	#run rm ${OUTPUT_FILE}
	#assert_success
}


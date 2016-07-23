.PHONY: all test clean
all: test clean

test:
	py.test --cov=by_isp_coverage by_isp_coverage/tests --cov-report html --cov-report xml --junitxml test_results.xml

clean:
	rm -r build by_isp_coverage.egg-info .cache .coverage coverage_html_report dist

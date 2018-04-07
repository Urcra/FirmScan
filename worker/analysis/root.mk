
dummy:
	python dummy.py > dummy.anal

analysis: dummy
	echo "looks good"

.PHONY: analysis

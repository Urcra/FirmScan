
unpack.flag:
	binwalk
	echo "ok" >> unpack.flag

dummy: unpack.flag
	python dummy.py > dummy.anal

analysis: dummy
	echo "looks good"

.PHONY: analysis unpack.flag

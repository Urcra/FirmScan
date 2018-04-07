unpack.flag:
	binwalk -Mre ./firmware.bin
	echo "ok" >> unpack.flag

dummy: unpack.flag
	python dummy.py > dummy.anal

analysis: dummy
	echo "looks good"

.PHONY: analysis unpack.flag

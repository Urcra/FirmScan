unpack.flag:
	binwalk -Mre ./firmware.bin
	echo "ok" >> unpack.flag

php: unpack.flag
	python checkPhp.py > php_reaper.anal

dummy: unpack.flag
	python dummy.py > dummy.anal

analysis: dummy
	echo "looks good"

.PHONY: php analysis unpack.flag
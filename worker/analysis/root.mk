unpack.flag:
	binwalk -e -M=20 ./firmware.bin
	echo "ok" >> unpack.flag

php: unpack.flag
	python checkPhp.py > php_reaper.anal

keys: unpack.flag
	python key-files.py _firmware.bin.extracted
	python key-strings.py _firmware.bin.extracted

dummy: unpack.flag
	python dummy.py > dummy.anal

analysis: dummy keys php
	echo "analysis completed"

.PHONY: analysis

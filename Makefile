freefare:
	# Hack to get around cffi not supporting #include directives
	clang -E libfreefare/libfreefare/freefare.h > freefare.h.preprocessed

nfc:
	clang -E libnfc/include/nfc/nfc.h > nfc.h.preprocessed
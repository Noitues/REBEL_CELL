class_name Png16
extends RefCounted
## NA-23c: a 16-bit grayscale PNG writer (Godot's `Image.save_png` is 8-bit only). The depth pass of the 12.0 capture needs 16 bits.

static var _crc_table := PackedInt64Array()


## Writes `bytes_be` (`w * h` big-endian 16-bit samples, row by row) as a grayscale 16-bit PNG at `path`. True on success.
static func save_gray16(path: String, w: int, h: int, bytes_be: PackedByteArray) -> bool:
	if bytes_be.size() != w * h * 2:
		return false
	var raw := PackedByteArray()
	var stride := w * 2
	raw.resize(h * (stride + 1))
	for y in h:
		raw[y * (stride + 1)] = 0  # filter: none
		var row := bytes_be.slice(y * stride, (y + 1) * stride)
		for i in stride:
			raw[y * (stride + 1) + 1 + i] = row[i]
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_buffer(PackedByteArray([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]))
	var ihdr := PackedByteArray()
	ihdr.append_array(_be32(w))
	ihdr.append_array(_be32(h))
	ihdr.append_array(PackedByteArray([16, 0, 0, 0, 0]))
	_chunk(f, "IHDR", ihdr)
	_chunk(f, "IDAT", raw.compress(FileAccess.COMPRESSION_DEFLATE))
	_chunk(f, "IEND", PackedByteArray())
	f.close()
	return true


## The 16-bit samples (R = high byte, G = low byte of each pixel) of `img` as big-endian bytes, row by row.
static func samples_from_rg(img: Image) -> PackedByteArray:
	var rg := img.duplicate() as Image
	rg.convert(Image.FORMAT_RG8)
	return rg.get_data()


static func _be32(v: int) -> PackedByteArray:
	return PackedByteArray([(v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255])


static func _chunk(f: FileAccess, kind: String, data: PackedByteArray) -> void:
	var body := kind.to_ascii_buffer()
	body.append_array(data)
	f.store_buffer(_be32(data.size()))
	f.store_buffer(body)
	f.store_buffer(_be32(_crc32(body)))


static func _crc32(data: PackedByteArray) -> int:
	if _crc_table.is_empty():
		_crc_table.resize(256)
		for n in 256:
			var c := n
			for _k in 8:
				c = (0xEDB88320 ^ (c >> 1)) if (c & 1) == 1 else (c >> 1)
			_crc_table[n] = c
	var crc := 0xFFFFFFFF
	for b in data:
		crc = _crc_table[(crc ^ b) & 255] ^ (crc >> 8)
	return crc ^ 0xFFFFFFFF

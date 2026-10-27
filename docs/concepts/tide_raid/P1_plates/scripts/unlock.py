import gpu_lock as GL
print('holder', GL.holder())
GL.release()
print('after', GL.holder())

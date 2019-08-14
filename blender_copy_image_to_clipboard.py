'''
Blender Script - Copy "Viewer Node" image to clipboard


- Windows only
- needs: Python module: Pillow (PIL), pywin32

base:
    a-nakanosora/blender_copy_image_to_clipboard.py
    https://gist.github.com/a-nakanosora/9493b14836fe054294ade772e1df8c68

ref:
    python - Copy PIL/PILLOW Image to Windows Clipboard - Stack Overflow
    http://stackoverflow.com/questions/21319486/copy-pil-pillow-image-to-windows-clipboard
    
    [Blender] スクリプト内部で自作の機能にショートカットキーを割り当てる
    https://qiita.com/nutti/items/e29226ff8bd7a7e770aa

    Blenderではじめる画像処理
    https://qiita.com/nacasora/items/cf0e27d38b09654cf701

    Write image to Windows clipboard in python with PIL and win32clipboard?
    https://stackoverflow.com/questions/7050448/write-image-to-windows-clipboard-in-python-with-pil-and-win32clipboard
'''


import bpy
import numpy as np
from PIL import Image, ImageOps
from io import BytesIO
import win32clipboard



bl_info = {
    "name": "Copy vewer node image to clipboard",
    "author": "skishida",
    "version": (0, 1),
    "blender": (2, 80, 75),
    "location": "View > Image",
    "description": "Copy vewer node image to clipboard \n need to adding ""vewer node"" to compositor node.",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "https://gist.github.com/skishida/4b682f385a65d3703e0d061dd9611e0d",
    "tracker_url": "",
    "category": "Render"
}

addon_keymaps = [] 

class CopyImageToClipboard_OT_copytoclipboard(bpy.types.Operator):
    bl_label="Send ViewerNode Image to Clipboard"
    bl_idname = "ci.sendtoclipboard"
    def send_to_clipboard(self, clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()

    def clipboard_copy_image(self, pimg):
        import io

        import ctypes
        msvcrt = ctypes.cdll.msvcrt
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        output = io.BytesIO()
        pimg.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()


        self.send_to_clipboard(win32clipboard.CF_DIB, data)
        
    def execute(self, context):
        print("yattarude")
        img0 = bpy.data.images['Viewer Node']
        W,H = img0.size
        
        pxs = img0.pixels[:]
        rw = np.array(pxs)

        # ガンマ補正(2.2固定)
        rw[0::4] = np.power(rw[0::4]/rw[3::4], 1/2.2)
        rw[1::4] = np.power(rw[1::4]/rw[3::4], 1/2.2)
        rw[2::4] = np.power(rw[2::4]/rw[3::4], 1/2.2)

        # Blender用ピクセルを0～255の整数に変換
        a = (rw*255).astype(np.int)
        a[a<0] = 0
        a[a>255] = 255
        a = a.astype(np.uint8)

        import array
        pimg = Image.frombytes("RGBA", (W,H),  array.array("B", a).tostring()  ) ## convert pixels(list) to bytes-stream
        pimg = ImageOps.flip(pimg)
        self.clipboard_copy_image(pimg)

        self.report({'INFO'}, 'copied the image to clipboard')
        return {'FINISHED'} 


classes = [
    CopyImageToClipboard_OT_copytoclipboard
]

def menu_func(self, context):
    self.layout.operator(CopyImageToClipboard_OT_copytoclipboard.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    # 登録するショートカットキーのリストを作成
    # (キーが押されたときに実行する bpy.types.Operator のbl_idname, キー, イベント, Ctrlキー, Altキー, Shiftキー)
    key_assign_list = [
        (CopyImageToClipboard_OT_copytoclipboard.bl_idname, "C", "PRESS", True, False, True),
    ]
    if kc:
        km = kc.keymaps.new(name="Image editor", space_type="IMAGE_EDITOR")    # 「IMAGE_EDITOR」のショートカットキーとして登録
        for (idname, key, event, ctrl, alt, shift) in key_assign_list:
            kmi = km.keymap_items.new(
                idname, key, event, ctrl=ctrl, alt=alt, shift=shift)    # ショートカットキーの登録
            addon_keymaps.append((km, kmi))



    bpy.types.IMAGE_MT_image.append(menu_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)    # ショートカットキーの登録解除
    addon_keymaps.clear()
    bpy.types.IMAGE_MT_image.remove(menu_func)



if __name__ == "__main__":
    register()
    
    # bpy.ops.ci.sendtoclipboard() #test
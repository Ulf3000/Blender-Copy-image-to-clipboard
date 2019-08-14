'''
Blender Script - Copy "Viewer Node" image to clipboard (for blender 2.8)

- Windows only
- needs: Python module: Pillow (PIL), pywin32

usage:
    - setup pillow and pywin32 package with pip
    - import this script as addon
    - add "Vewer" node to  compositor and link it
    - cick "Send ViewerNode Image to Clipboard" on "View > Image" menu.


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

todo:
    - 最新のレンダリング結果を取れないことがある(レンダリング中断時等) ref: https://developer.blender.org/T54314
    - 虚無を入力したときに発生する `RuntimeWarning: invalid value encountered in true_divide`
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

class testst_OT_testset(bpy.types.Operator):
    bl_label="testshortcut"
    bl_idname = "test.key"
    
    def execute(self, context):
        self.report({'INFO'}, 'UGOKU')
        return {'FINISHED'} 

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
        scene = bpy.context.scene
        scene.render.use_compositing = True

        img0 = bpy.data.images['Viewer Node']
        W,H = img0.size

        print("{w},{h}".format(w=W, h=H))

        if W == 0 & H == 0:
            self.report({'WARNING'}, 'no image for copy, are vewer node exist & connected ?')
            return {'CANCELLED'}
        
        pxs = img0.pixels[:]
        rw = np.array(pxs)

        print(rw)

        if np.any(np.isnan(rw)):
            self.report({'WARNING'}, 'some data types are wrong')
            return {'CANCELLED'}

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
    CopyImageToClipboard_OT_copytoclipboard,
    testst_OT_testset
]

def menu_func(self, context):
    self.layout.operator(CopyImageToClipboard_OT_copytoclipboard.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.IMAGE_MT_image.append(menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    # 登録するショートカットキーのリストを作成
    # (キーが押されたときに実行する bpy.types.Operator のbl_idname, キー, イベント, Ctrlキー, Altキー, Shiftキー)
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new(CopyImageToClipboard_OT_copytoclipboard.bl_idname, 'C', 'PRESS', ctrl=True, shift=False)
        addon_keymaps.append((km, kmi))
        # kmi = km.keymap_items.new(testst_OT_testset.bl_idname, 'C', 'PRESS',  ctrl=True)
        # addon_keymaps.append((km, kmi))






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
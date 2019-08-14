# Blender Script - Copy "Viewer Node" image to clipboard (for blender 2.8)

- Windows only
- needs: Python module: Pillow (PIL), pywin32

## usage
1. setup pillow and pywin32 package with pip
2.  import this script as addon
3.  add "Vewer" node to  compositor and link it
4.  cick "Send ViewerNode Image to Clipboard" on "View > Image" menu.
    * or press Ctrl+Shift+C on Image Editor

![](anim.gif)

## base

* a-nakanosora/blender_copy_image_to_clipboard.py
  * https://gist.github.com/a-nakanosora/9493b14836fe054294ade772e1df8c68

## ref

* python - Copy PIL/PILLOW Image to Windows Clipboard - Stack Overflow
  * http://stackoverflow.com/questions/21319486/copy-pil-pillow-image-to-windows-clipboard
    
* [Blender] スクリプト内部で自作の機能にショートカットキーを割り当てる
  * https://qiita.com/nutti/items/e29226ff8bd7a7e770aa

* Blenderではじめる画像処理
  * https://qiita.com/nacasora/items/cf0e27d38b09654cf701

* Write image to Windows clipboard in python with PIL and win32clipboard?
  * https://stackoverflow.com/questions/7050448/write-image-to-windows-clipboard-in-python-with-pil-and-win32clipboard

## todo
  
* 最新のレンダリング結果を取れないことがある(レンダリング中断時等) ref: https://developer.blender.org/T54314
* 虚無を入力したときに発生する `RuntimeWarning: invalid value encountered in true_divide`

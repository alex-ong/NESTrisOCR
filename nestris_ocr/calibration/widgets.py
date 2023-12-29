import platform

if platform.system() == "Darwin":
    import tkmacosx

    class Button(tkmacosx.Button):
        def __init__(self, *args, **kwargs):
            if "width" in kwargs:
                kwargs["width"] = kwargs["width"] * 15
                # convert character width to pixel width. Sigh...

            super(Button, self).__init__(*args, **kwargs)

else:
    from tkinter import Button

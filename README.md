Code that provides a similar interface to that of Tex in manim

 Here's an example:
```py
class Test(Scene):
    def construct(self):
        frame_ = _Typst(r"""
                        #{title}[== Introduction]
                        $ {int}(integral)_0^({u}(1)) x d x = lr(x^2/2|)_0^1 $
                        """)
        frame_['title'].set_color(RED)

        frame_['int'].set_color(YELLOW)
        
        frame_['u'].set_color(GREEN)

        self.add(frame_)
```

![Image](https://github.com/user-attachments/assets/8e2d7511-3250-42a7-8f3e-1dced26ece52)


The idea of how I made the "groups"(can be nested) is that I hid (via #hide in Typst) the desired part and then subtracted it from the whole scene.

import hashlib
from pathlib import Path
from manim import SVGMobject, config, VGroup
import typst
from string import Formatter
import numpy as np
# from dataclasses import dataclass

class _typst(SVGMobject):
    def __init__(
            self, text: str, 
            page_fill: str = "none",
            page_width: str = f"{config.frame_width}cm",
            page_height: str = f"{config.frame_height}cm",
            spread_width: bool = True,
            text_fill: str = "white",
            text_size: int = 9,
            center: bool = False,
            # margin: MarginL
            preambular: str | None = None
                ):
        # Generate the Typst code
        if center:
            text = f"#align(center+horizon)[{text}]"
        if preambular is not None:
            code = preambular + '\n' + text
        else:
            code = f"""
                #set page(width: {page_width}, height: {page_height}, fill: {page_fill}, background: rect(height: 100%, width: 100%), margin: (left: 0.7cm, top: 0.8cm, bottom: 0.1cm, right: 0.7cm))
                #set text(fill: {text_fill}, size: {text_size}pt)                        
                """+ text

        # Hash the code
        hash_object = hashlib.sha256(code.encode())
        hash_hex = hash_object.hexdigest()

        # Define directories
        typ_dir = Path("media/typst/typ_code")
        svg_dir = Path("media/typst/svg")

        # Ensure directories exist
        typ_dir.mkdir(parents=True, exist_ok=True)
        svg_dir.mkdir(parents=True, exist_ok=True)

        # Define file paths
        typ_file = typ_dir / f"{hash_hex}.typ"
        svg_file = svg_dir / f"{hash_hex}.svg"

        # Check if the SVG file already exists
        if not svg_file.exists():
            # Write the Typst code to the .typ file
            typ_file.write_text(code, encoding="utf-8")

            # Compile the Typst code to an SVG
            typst.compile(input=str(typ_file), output=str(svg_file), format="svg")

        # Initialize the SVGMobject with the compiled SVG path
        super().__init__(str(svg_file))


        
        if spread_width:
            self.set_width(config.frame_width)

        self.remove(self.submobjects[0])

class Typst(VGroup):
    def __init__(   self, *parts,
                    before: str = "",
                    after: str = "", 
                    separator: str = "\n",
                    page_fill: str = "none",
                    page_width: str = f"{config.frame_width}cm",
                    page_height: str = f"{config.frame_height}cm",
                    spread_width: bool = True,
                    text_fill: str = "white",
                    text_size: int = 9,
                    center: bool = False,
                    preambular: str | None = None):
        N = len(parts)
        if N == 0:
            super().__init__(*parts)
            return
        vmobjs = []
        for i in range(N):
            if i==0:
                text = parts[0] + separator + "#hide[" + separator.join(parts[1:]) +"]"
            elif i==N-1:
                text = "#hide[" + separator.join(parts[:-1]) + "]" +separator+ parts[-1]
            else:
                text =  "#hide[" + separator.join(parts[:i]) + "]" +separator+ parts[i]+separator +"#hide[" + separator.join(parts[i+1:]) + "]"
            text = before + separator + text + separator + after
            vmobjs.append(_typst(
                    text,
                    page_fill = page_fill,
                    page_width=page_width,
                    page_height= page_height,
                    spread_width =spread_width,
                    text_fill=text_fill,
                    text_size=text_size,
                    center  = center,
                    preambular = preambular
            ))

        super().__init__(*vmobjs)


class Typst2(_typst):
    def __init__(self, group_text: str):
        formatter = Formatter()
        placeholders = sorted([item[1] for item in formatter.parse(group_text) if item[1] is not None])
        N_groups = len(placeholders)

        def how_many_to_hide(arr):
            value_list = []
            value_dict= dict()
            for j, item in enumerate(placeholders):
                what: str = 'id'
                if j in arr:
                    what = 'notId'
                if item == "":
                    value_list.append(what)
                else:
                    value_dict[item] = (what)
            return group_text.format(*value_list, **value_dict)
            


        preambular=r"""
                    #let id(it)={it}
                    #let notId(it)={hide[#it]}
                    """


        super().__init__(preambular+ how_many_to_hide([]))

        self.__list_of_hidden = []


        def A_minus_B(A, B):
            def is_identical_path(mob1, mob2):
                points1 = mob1.get_points()
                points2 = mob2.get_points()

                if points2.shape != points1.shape:
                    return False
                return np.linalg.norm(points1 - points2)<10**-5
            return    VGroup(
                            *[m for m in A.submobjects if not any(is_identical_path(m, p) for p in B.submobjects)]
                        )


        for i in range(N_groups):
            code = how_many_to_hide([i])
            item = placeholders[i]
            el_minus = _typst(preambular+code)
            # print(code, placeholders[i])
            self.__list_of_hidden.append((A_minus_B(self, el_minus), item))
        self.groups = [el[0] for el in self.__list_of_hidden]

    def without(A: SVGMobject, B:SVGMobject):
        def is_identical_path(mob1, mob2):
            points1 = mob1.get_points()
            points2 = mob2.get_points()

            if points2.shape != points1.shape:
                return False
            return np.linalg.norm(points1 - points2)<10**-5
        return    VGroup(
                        *[m for m in A.submobjects if not any(is_identical_path(m, p) for p in B.submobjects)]
                    )

    def __getitem__(self, key):
        if isinstance(key, str):
            for el in self.__list_of_hidden:
                if el[1] == key:
                    return el[0]
            raise KeyError(f"No object found with name '{key}'")
        if isinstance(key, tuple) and all(isinstance(item, str) for item in key) :
            temp = VGroup()
            absent = []
            for item in key:
                for el in self.__list_of_hidden:
                    if el[1] == item:
                        temp.add(el[0])
                        break
                else:
                    absent.append(item)
            if len(absent)==0:
                return temp
            raise KeyError(f"No object(s) found with name(s) '{absent}'")
        return super().__getitem__(key)


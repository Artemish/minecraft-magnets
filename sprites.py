from os import system, listdir
import json
import re
import subprocess

from PIL import Image


def get_tiles(d):
    lst = listdir(d)
    regex = re.compile(".*.png")
    for f in lst:
        if (regex.match(f)):
            yield f

def get_sheets(d):
    lst = listdir(d)
    regex = re.compile("sheet_\d+.png")
    for f in lst:
        if (regex.match(f)):
            yield f

def gen_names():
    json_obj = {}
    for tile in get_tiles():
        p = subprocess.Popen(['display', tile])
        print("Title the sprite (empty for none): ")
        name = input()
        p.kill()
        if name != '':
            system("mv {0} named/{1}.png".format(tile, name))
            json_obj[name] = 0
        else:
            system("rm {0}".format(tile))

    write_json(json_obj, 'initial_counts.json')

def write_json(obj, fname):
    # Parameters for pretty print
    data = json.dumps(obj, sort_keys=True,indent=4,separators=(',', ': '))
    f = open(fname, 'w')
    f.write(data)
    f.close()

def gen_initial_counts(count_file):
    count_obj = {}
    for d in ['items', 'named']:
        for f in get_tiles(d):
            path = d + '/' + f
            count_obj[path] = 0
    write_json(count_obj, count_file)

def get_counts(count_file):
    f = open(count_file, 'r')
    return json.loads(f.read())

def populate_images(counts):
    container = {}
    for path in counts:
        img = Image.open(path)
        assert(img.size == (96, 96))
        container[path] = img

    return container

# If someone knows a more pythonic method I'm all ears
# Generate a list of 2d width x height sheets
def pack_into_lists(counts, width, height):
    all_counts = [[key]  * counts[key]  for key in counts]
    all_num = []
    for count_group in all_counts:
        all_num.extend(count_group)
    by_sheet = [all_num[x:x+width*height] for x in range(0, len(all_num), width*height)]

    sheets = []
    for sheet in by_sheet:
        rows = [sheet[x:x+width] for x in range(0, len(sheet), width)]
        sheets.append(rows)

    return sheets

def generate_sprite_sheets(sheets, images, width, height, side_length):
    sheet_images = []
    for sheet_index, sheet in enumerate(sheets):
        # RGBA for RGB + alpha channel
        sheet_image = Image.new(mode='RGBA',
                size = (width * side_length, height * side_length),
                color = (0, 0, 0, 0)) # Initially transparent

        for row_index, row in enumerate(sheet):
            top = row_index * side_length 
            for column_index, image_path in enumerate(row):
                i = images[image_path]
                left = column_index * side_length
                sheet_image.paste(i, (left, top))

        sheet_images.append(sheet_image)

    return sheet_images

def main():
    count_file = "counts.json"
    side_length = 96
    width, height = 8, 10

    counts = get_counts(count_file)
    pil_images = populate_images(counts)
    sheets = pack_into_lists(counts, width, height)
    sheet_images = generate_sprite_sheets(sheets, pil_images, width, height, side_length)

    guide = Image.open("./guide_transparency.png")

    for sheet_index, sheet_image in enumerate(sheet_images):
        filename = "output/sheet_{0}.png".format(sheet_index)
        guided_filename = "output/guided_sheet_{0}.png".format(sheet_index)
        sheet_image.save(filename)
        guide.paste(sheet_image, (6, 32))
        guide.save(guided_filename)

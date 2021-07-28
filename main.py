import json
from PIL import Image, ImageDraw, ImageFont


def connect_points(draw, points, color, height_change, width_change):
    points[0][0] = int(points[0][0] * height_change)
    points[0][1] = int(points[0][1] * width_change)
    for i in range(1, len(points)):
        # Recalculating the points based on height/width change, dictionary is then saved in a json
        points[i][0] = int(points[i][0] * height_change)
        points[i][1] = int(points[i][1] * width_change)
        draw.line([(points[i - 1][0], points[i - 1][1]),
                   (points[i][0], points[i][1])], color)

    # Connect last point with first point
    draw.line([(points[-1][0], points[-1][1]),
               (points[0][0], points[0][1])], color)


def draw_shapes(lesions, image, height_change, width_change):
    draw = ImageDraw.Draw(image)
    for properties in lesions.values():
        points = properties['pointsList']
        color = properties["ClassColorName"]
        if len(points) == 0:
            continue
        connect_points(draw, points, color, height_change, width_change)

        width, height = image.size
        x_offset, y_offset = int(width / 256), int(height / 256)
        text_coord = (points[0][0] + x_offset, points[0][1] + y_offset)
        text = properties['Name']
        font_size = int(properties['fontSize'] * 10)  # Not sure about font size
        font = ImageFont.truetype("arial.ttf", font_size)

        draw.text(text_coord, text, color, font=font)


def handle_input():
    image_path = input("Path to retina image: ")
    json_path = input("Json with annotation: ")
    print("Target dimensions of the image: ", end="")
    try:
        x, y = map(int, input().split())
        new_size = (x, y)
        if x <= 0 or y <= 0:
            print("Height and width must be > 0.")
            print("Aborting script...")
            return
    except ValueError:
        print("Invalid target dimensions.")
        print("Aborting script...")
        return

    try:
        with open(json_path) as f1:
            data = json.load(f1)

        image = Image.open(image_path)
    except (FileNotFoundError, PermissionError):
        print("Error handling files")
        print("Aborting script...")
        return

    return image, data, new_size


def main():
    try:
        image, data, new_size = handle_input()
    except TypeError:
        return

    lesions = data['segmentedObjectDict']
    image_resize = image.resize(new_size)
    image_resize.save("resize.jpg")

    width, height = image.size
    width_change, height_change = new_size[0] / width, new_size[1] / height
    draw_shapes(lesions, image_resize, width_change, height_change)

    image_resize.save('result.jpg')

    with open('result.json', 'w') as f2:
        json.dump(data, f2, indent=2)

    print("Success!")


if __name__ == "__main__":
    main()

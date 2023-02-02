
import scribe

def print_get_reflection_degree():
    canvas = scribe.Canvas(30, 30)
    s = scribe.TerminalScribe(canvas)

    for w in scribe.Wall:
        print(w)
        for i in range(360):
            r = s.get_reflection_degree(w, i)
            if r != -1:
                print(i,' =>', r)

if __name__ == '__main__':
    print_get_reflection_degree()
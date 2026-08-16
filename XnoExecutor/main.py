import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xno_app import XnoApp


def main():
    app = XnoApp()
    app.mainloop()


if __name__ == "__main__":
    main()

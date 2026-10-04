"""Remove this round's own scratch folder (and only that path)."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(os.path.dirname(HERE), 'scratch')

if __name__ == '__main__':
    assert os.path.basename(os.path.dirname(SCR)) == 'round32_ui_chrome'
    if os.path.isdir(SCR):
        shutil.rmtree(SCR)
        print('removed', SCR)

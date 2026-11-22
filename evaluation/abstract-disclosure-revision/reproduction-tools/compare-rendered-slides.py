from pathlib import Path
import json
from PIL import Image, ImageChops

W = Path(__file__).parent
baseline = W.parent / '.submission-grader-attribution-review/native-slides'
changed = set(json.loads((W / 'slide-map.json').read_text(encoding='utf-8'))['changed'])
results = []
for n in range(1, 50):
    current = Image.open(W / 'native-slides' / f'Slide{n}.PNG').convert('RGB')
    original = Image.open(baseline / f'Slide{n}.PNG').convert('RGB')
    assert current.size == original.size
    diff = ImageChops.difference(current, original)
    results.append({'slide': n, 'intended_change': n in changed,
                    'pixels_identical': diff.getbbox() is None,
                    'difference_bounds': diff.getbbox()})
unintended = [row for row in results if not row['intended_change'] and not row['pixels_identical']]
out = {'slides': results,
       'unchanged_slides_identical': sum(not row['intended_change'] and row['pixels_identical'] for row in results),
       'unintended_differences': unintended}
(W / 'render-comparison.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({'unchanged_slides_identical': out['unchanged_slides_identical'],
                  'unintended_differences': unintended}, indent=2))
assert not unintended

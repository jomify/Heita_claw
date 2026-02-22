from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_STRATEGIES = {'mean', 'median', 'mean_median_blend'}


def main() -> None:
    parser = argparse.ArgumentParser(description='Build Kaggle kernel files for one experiment (GPU-side run).')
    parser.add_argument('--username', required=True)
    parser.add_argument('--slug', required=True)
    parser.add_argument('--strategy', default='mean_median_blend', choices=sorted(VALID_STRATEGIES))
    parser.add_argument('--blend-alpha', type=float, default=0.7)
    parser.add_argument('--title', default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    kernel_dir = project_root / 'kaggle_kernel'

    template = (kernel_dir / 'main_template.py').read_text(encoding='utf-8')
    rendered = template.replace('__STRATEGY__', args.strategy).replace('__BLEND_ALPHA__', str(args.blend_alpha))
    (kernel_dir / 'main.py').write_text(rendered, encoding='utf-8')

    metadata = {
        'id': f'{args.username}/{args.slug}',
        'title': args.title or args.slug,
        'code_file': 'main.py',
        'language': 'python',
        'kernel_type': 'script',
        'is_private': True,
        'enable_gpu': True,
        'enable_internet': True,
        'competition_sources': ['stanford-rna-3d-folding-2'],
    }
    (kernel_dir / 'kernel-metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Prepared experiment kernel:', metadata['id'])


if __name__ == '__main__':
    main()

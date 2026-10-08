import hashlib
import os
import os.path as osp
import sys

from setuptools import Extension, setup, find_packages
from torch.utils.cpp_extension import BuildExtension, CUDAExtension, include_paths, library_paths

ROOT = osp.dirname(osp.abspath(__file__))
MAST3R = 'thirdparty/mast3r'
CUROPE = 'thirdparty/mast3r/dust3r/croco/models/curope'
ASMK = 'thirdparty/mast3r/asmk'
PYIMGUI = 'thirdparty/in3d/thirdparty/pyimgui'

torch_include_dirs = include_paths()
torch_library_dirs = library_paths()
conda_prefix = os.environ.get("PREFIX", os.environ.get("CONDA_PREFIX", ""))
eigen_path = osp.join(conda_prefix, 'include', 'eigen3')


class BuildExt(BuildExtension):
    """torch's BuildExtension, with one build directory per environment: pixi builds the CUDA variants in
    parallel from this same source tree, and they must not share object files."""

    def finalize_options(self):
        super().finalize_options()
        self.build_temp = osp.join(self.build_temp, hashlib.sha1(sys.prefix.encode()).hexdigest()[:10])


def pyimgui_extension(name):
    # pyimgui's own setup.py, building from its pre-generated C++ (it needs Cython<0.30 to regenerate them)
    return Extension(
        f'imgui.{name}',
        sources=[f'{PYIMGUI}/imgui/{name}.cpp'] + [f'{PYIMGUI}/{src}' for src in (
            'imgui-cpp/imgui.cpp', 'imgui-cpp/imgui_draw.cpp', 'imgui-cpp/imgui_demo.cpp',
            'imgui-cpp/imgui_widgets.cpp', 'imgui-cpp/imgui_tables.cpp', 'config-cpp/py_imconfig.cpp')],
        include_dirs=[osp.join(ROOT, PYIMGUI, d) for d in ('imgui', 'config-cpp', 'imgui-cpp', 'ansifeed-cpp')],
        define_macros=[('PYIMGUI_CUSTOM_EXCEPTION', None)],
        extra_compile_args=['-include', osp.join(ROOT, PYIMGUI, 'config-cpp', 'py_imconfig.h')],
    )


# Package metadata and console scripts live in pyproject.toml; setup.py declares packages and extensions.
# GPU targets of the CUDA extensions come from TORCH_CUDA_ARCH_LIST (defaults to the build machine's GPU).
setup(
    packages=find_packages(where='.') +
        find_packages(where=MAST3R, include=["mast3r", "mast3r.*", "dust3r", "dust3r.*"]) +
        find_packages(where='thirdparty/in3d', include=["in3d", "in3d.*"]) +
        find_packages(where=ASMK, include=["asmk", "asmk.*"]) +
        find_packages(where=PYIMGUI, include=["imgui", "imgui.*"]),
    package_dir={
        'mast3r': f'{MAST3R}/mast3r',
        'dust3r': f'{MAST3R}/dust3r',
        'in3d': 'thirdparty/in3d/in3d',
        'asmk': f'{ASMK}/asmk',
        'imgui': f'{PYIMGUI}/imgui',
    },
    include_package_data=True,
    package_data={
        'mast3r_slam': ['resources/programs/*.glsl'],
        'in3d': ['resources/programs/*.glsl'],
        'mast3r_slam.configs': ['*.yaml'],
    },
    ext_modules=[
        CUDAExtension(
            name='mast3r_slam_backends',
            include_dirs=torch_include_dirs + [
                osp.join(ROOT, 'mast3r_slam/backend/include'),
                eigen_path
                ],
            library_dirs=torch_library_dirs,
            sources=[
                'mast3r_slam/backend/src/gn.cpp',
                'mast3r_slam/backend/src/gn_kernels.cu',
                'mast3r_slam/backend/src/matching_kernels.cu',
            ],
            extra_compile_args={
                'cxx': ['-O3', '-D_GLIBCXX_USE_CXX11_ABI=1'],
                'nvcc': ['-O3'],
            }
        ),
        CUDAExtension(  # CroCo's RoPE kernels; without them dust3r falls back to a slow pytorch RoPE2D
            name='curope',
            sources=[f'{CUROPE}/curope.cpp', f'{CUROPE}/kernels.cu'],
            extra_compile_args={'cxx': ['-O3'], 'nvcc': ['-O3', '--use_fast_math']},
        ),
        Extension('asmk.hamming', [f'{ASMK}/cython/hamming.c']),
        pyimgui_extension('core'),
        pyimgui_extension('internal'),
    ],
    cmdclass={'build_ext': BuildExt.with_options(no_python_abi_suffix=True)},
)

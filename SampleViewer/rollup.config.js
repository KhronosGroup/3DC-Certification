import glslify from 'rollup-plugin-glslify';
import resolve from 'rollup-plugin-node-resolve';
import builtins from 'rollup-plugin-node-builtins';
import scss from 'rollup-plugin-scss';
import commonjs from 'rollup-plugin-commonjs';
import copy from 'rollup-plugin-copy';
import alias from '@rollup/plugin-alias';
import replace from '@rollup/plugin-replace';

export default {
  input: 'src/main.js',
  output: [
    {
      name: 'SampleViewerApp',
      file: 'dist/GltfSVApp.umd.js',
      format: 'umd',
      sourcemap: true,
      external: [ 'gl-matrix', 'axios', 'jpeg-js', 'fast-png']
    }
  ],
  plugins: [
    commonjs({

    }),
    glslify({
        include: ['../source/Renderer/shaders/*', '../source/shaders/*'],
        compress: false
    }),
    resolve({
        browser: true,
        preferBuiltins: true
    }),
    builtins(),
    scss(),
    copy({
        targets: [
            { src: ["index.html"], dest: "dist/"},
            { src: ["../assets/models/2.0", "!../asset/models/.git"], dest: "dist/assets/models"},
            { src: ["../assets/environments/*.hdr", "../assets/environments/*.jpg", "!../asset/environments/.git"], dest: "dist/assets/environments"},
            { src: ["ui"], dest: "dist/assets"},
            { src: ["images"], dest: "dist/assets"},
            { src: ["node_modules/@khronosgroup/gltf-viewer/dist/libs/*", "!../source/libs/hdrpng.js"], dest: "dist/libs"},
            { src: ["node_modules/@khronosgroup/gltf-viewer/dist/assets/*"], dest: "dist/assets/images"}
        ],
        copyOnce: true,
        verbose: true
    }),
    replace({
      'process.env.NODE_ENV': JSON.stringify( 'production' )
    }),
    alias({
      'vue': 'vue/dist/vue.esm.js'
    }),
  ]
};

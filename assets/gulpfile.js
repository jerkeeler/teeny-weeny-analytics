const gulp = require('gulp');
const uglify = require('gulp-uglify');
const pump = require('pump');

gulp.task('compress', (cb) => {
  pump([
        gulp.src('src/collect.js'),
        uglify(),
        gulp.dest('dist/v1'),
    ],
    cb,
  );
});

gulp.task('copy', (cb) => {
  pump([
    gulp.src('src/collect.js'),
    gulp.dest('dist'),
  ]);
});

var gulp = require('gulp'),
    sass = require('gulp-sass'),
    notify = require('gulp-notify'),
    filter = require('gulp-filter'),
    autoprefixer = require('gulp-autoprefixer'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    livereload = require('gulp-livereload'),
    connect = require('connect'),
    serveIndex = require('serve-index'),
    serveStatic = require('serve-static'),
    sourcemaps = require("gulp-sourcemaps"),
    babel = require("gulp-babel");

var config = {
    stylesPath: 'theme/styles/',
    jsPath: 'theme/scripts/',
    imagesPath: 'theme/images/',
    outputDir: 'assets/'
};


gulp.task('icons', function () {
    return gulp.src('./node_modules/font-awesome/fonts/**.*')
        .pipe(gulp.dest(config.outputDir + 'fonts'));
});


gulp.task('fonts', function () {
    return gulp.src('assets/fonts/**.*')
        .pipe(gulp.dest(config.outputDir + 'fonts'));
});

gulp.task('images', function () {
    return gulp.src(config.imagesPath + '/*')
        .pipe(imagemin())
        .pipe(gulp.dest(config.outputDir + 'images'));
});

gulp.task('css', function () {
    return gulp.src(config.stylesPath + '*.scss')
        .pipe(sass({
            outputStyle: 'nested',
            sourceComments: true,
            includePaths: [
                config.stylesPath,
                './node_modules'
            ]
        }).on('error', sass.logError))
        .pipe(autoprefixer())
        .pipe(gulp.dest(config.outputDir + 'css'));
});


gulp.task('assets', function (done) {
    var scirpts = [
        './node_modules/jquery/dist/jquery.min.js',
        './node_modules/jquery-easing/jquery.easing.1.3.js',
        './node_modules/bootstrap/dist/js/bootstrap.js',
    ];

    gulp.src(scirpts)
        .pipe(gulp.dest(config.outputDir + 'js'));

    done();
});

gulp.task('js', function () {
    return gulp.src(config.jsPath + '*')
        .pipe(filter('**/*.js'))
        .pipe(sourcemaps.init())
        .pipe(babel())
        .pipe(concat('main.js'))
        .pipe(uglify())
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(config.outputDir + 'js'));
});

gulp.task('watch', function (done) {
    gulp.watch([config.stylesPath + '**/*.scss', config.stylesPath + '**/*.sass', config.stylesPath + '**/*.css'], gulp.series('css'));
    gulp.watch([config.jsPath + '**/*.js'], gulp.series('js'));
    gulp.watch([config.imagesPath + '/**/*'], gulp.series('images'));
    done();
});

gulp.task('connect', function () {

    var serveApp = serveStatic('public');
    var serveWhich = 'public';

    var app = connect()
        .use(require('connect-livereload')({port: 35729}))
        .use(serveStatic(serveWhich))
        .use(serveApp)
        .use(serveIndex(serveWhich));

    require('http').createServer(app)
        .listen(9000)
        .on('listening', function () {
            console.log('Started connect web server on http://localhost:9000.');
        });
});

gulp.task('serve', gulp.series('connect', 'watch', function () {

    livereload.listen();

    require('opn')('http://localhost:9000');

    var delay_livereload = function (timeout) {
        return function (vinyl) {
            setTimeout(function () {
                livereload.changed(vinyl);
            }, timeout);
        };
    };

    gulp.watch(['public/**/*']).on('change', delay_livereload(500));
    done();
}));

gulp.task('default', gulp.series('icons', 'fonts', 'images', 'css', 'assets', 'js', function (done){
    done();
}));

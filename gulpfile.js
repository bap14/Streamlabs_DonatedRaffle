var ChatBotInstallPath = 'D:\\Program Files (x86)\\AnkhBotR2',
    lineReader = require('line-by-line'),
    gulp = require('gulp'),
    version,
    zip = require('gulp-zip');

gulp.task('deploy', function () {
    getScriptSources()
        .pipe(gulp.dest(ChatBotInstallPath + '\\Services\\Scripts\\DonatedRaffle'));
});

gulp.task('bundle', function () {
    getCurrentVersion().then(
        function (version) {
            getScriptSources()
                .pipe(zip('DonatedRaffle-' + version + '.zip'))
                .pipe(gulp.dest('dist'));
        },
        function (err) { throw err; }
    )
});

function getScriptSources() {
    return gulp.src([
        '*.py',
        'settings.json',
        'README.md',
        'UI_Config.json',
        'settings.json'
    ]);
}

function getCurrentVersion() {
    return new Promise(function (resolve, reject) {
        var lr = new lineReader('DonatedRaffle_StreamlabsSystem.py'),
            that = this;
        this.isResolved = false;

        lr.on('line', function (line) {
            var matches = line.match(/^Version = "([^"]+)"$/);
            if (matches && matches.length === 2) {
                that.isResolved = true;
                lr.close();
                resolve(matches[1]);
            }
        });

        lr.on('error', function (err) {
            reject(err);
        });

        lr.on('end', function () {
            if (that.isResolved === false) {
                reject('Failed to find version line in python script');
            }
        })
    });
}
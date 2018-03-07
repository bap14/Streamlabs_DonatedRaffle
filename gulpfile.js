var ChatBotInstallPath = 'D:\\Program Files (x86)\\AnkhBotR2',
    lineReader = require('line-by-line'),
    gulp = require('gulp'),
    exec = require('gulp-exec'),
    os = require('os'),
    zip = require('gulp-zip');

gulp.task('compile', function () {
    compile();
});

gulp.task('execute', function () {
    execute();
});

gulp.task('compile-and-run', function () {
    compile().then(function () {
        console.log('Done compiling, time to execute!');
        execute();
    });
});

gulp.task('deploy', function () {
    getScriptSources()
        .pipe(gulp.dest(ChatBotInstallPath + '\\Services\\Scripts\\DonatedRaffle'));
});

gulp.task('bundle', function () {
    getCurrentVersion().then(
        function (version) {
            getScriptSources()
                .pipe(zip('Streamlabs Chatbot DonatedRaffle-' + version + '.zip'))
                .pipe(gulp.dest('dist'));
        },
        function (err) { throw err; }
    )
});

function compile() {
    return new Promise(function (resolve, reject) {
        var exePath = "C:\\Program Files\\NSIS\\makensis.exe";
        if (os.arch() == "x64") {
            exePath = "C:\\Program Files (x86)\\NSIS\\makensis.exe";
        }

        gulp.src('./nsis/DonatedRaffle.nsi')
            .pipe(exec('"' + exePath + '" /V4 "<%= file.path %>"'))
            .on('error', function () { reject(); })
            .on('end', function () { console.log('Finished pipeline'); resolve(); })
            .pipe(exec.reporter());
    });
}

function execute() {
    getCurrentVersion().then(
        function(version) {
            gulp.src('./dist/Streamlabs Chatbot Donated Raffle Setup-' + version + '.exe')
                .pipe(exec('"<%= file.path %>"'))
                .pipe(exec.reporter());
        }
    );
}

function getScriptSources() {
    return gulp.src([
        '*.py',
        'LICENSE',
        'README.md',
        'UI_Config.json'
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
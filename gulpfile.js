'use strict';

// requirements
var gulp = require('gulp'),
    args = require('yargs').argv,
    spawn = require('child_process').spawn,
    node;


var log_level = args.logging ? args.logging : 'info';
var vera_ip = args.vera_ip ? args.vera_ip : '0.0.0.0';
var vera_auth = args.auth ? args.auth : 'False';
var vera_auth_user = args.vera_auth_user ? args.vera_auth_user : 'None';
var vera_auth_passwd = args.vera_auth_passwd ? args.vera_auth_passwd : 'None';

/**
 * $ gulp server
 * description: launch the server. If there's a server already running, kill it.
 */
gulp.task('server', function () {
    if (node) node.kill()
    node = spawn('python',
        [
            'project/main.py',
            '--logging=' + log_level,
            '--vera_auth=' + vera_auth,
            '--vera_ip=' + vera_ip,
            '--vera_auth_user=' + vera_auth_user,
            '--vera_auth_passwd=' + vera_auth_passwd
        ],
        {stdio: 'inherit'})
    node.on('close', function (code) {
        if (code === 8) {
            gulp.log('Error detected, waiting for changes...');
        }
    });
})

gulp.task('watch', function () {
    gulp.watch(['project/main.py',
        'project/smarthome/**/*.py',
        'project/static/**/*.js'], ['server'])
})
/**
 * $ gulp
 * description: start the development environment
 */
gulp.task('default', ['server', 'watch'])


// clean up if an error goes unhandled.
process.on('exit', function () {
    if (node) node.kill()
})

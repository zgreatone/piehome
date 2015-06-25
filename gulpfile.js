'use strict';

// requirements
var gulp = require('gulp'),
    args = require('yargs').argv,
    spawn = require('child_process').spawn,
    node;


var log_level = args.logging ? args.logging : 'info';

/**
 * $ gulp server
 * description: launch the server. If there's a server already running, kill it.
 */
gulp.task('server', function () {
    if (node) node.kill()
    node = spawn('python', ['project/main.py', ['--logging=' + log_level]], {stdio: 'inherit'})
    node.on('close', function (code) {
        if (code === 8) {
            gulp.log('Error detected, waiting for changes...');
        }
    });
})

gulp.task('watch', function () {
    gulp.watch(['project/main.py', 'project/static/**/*.js'], ['server'])
})
/**
 * $ gulp
 * description: start the development environment
 */
//gulp.task('default', function() {
//  gulp.run('server')
//
//  gulp.watch(['project/main.py', 'project/static/**/*.js'], function() {
//    gulp.run('server')
//  })
//
//})

gulp.task('default', ['server', 'watch'])


// clean up if an error goes unhandled.
process.on('exit', function () {
    if (node) node.kill()
})

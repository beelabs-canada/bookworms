#!/usr/bin/env perl
use v5.12;
use warnings;

use CGI;
use CGI::Carp;
use Path::Tiny;

use constant PEOL => "\n"; # an easier way to write perl end of line

my ( $path, $pid, $session ) = stage();

# ==================================================
# PREQUISTES - lets check to see we have everything we need
# ==================================================
if ( ! $path->sibling( '.'.$pid )->is_dir )
{
	error($session, 'cannot start application .. missing a program folder [.'.$pid.']' );
}

# ==================================================
# INITIALIZATION - Lets get a build dir and load
# 		dependencies
# ==================================================

my ( $build,   ) = pollenate( $path->sibling( '.'.$pid ) );


print "PID: " , $pid, PEOL;
print "QUERY: limit -> ", scalar $session->param('limit'), PEOL;





# ============================================
# FUNCTIONS
# ============================================

# @function - stage
# @param - none
# @returns {array} - initial enviroment variables
sub stage
{
	require CGI;
	require CGI::Carp;
	require Path::Tiny;

	my $path = Path::Tiny::path( $0 )->absolute;
	my $pid = $path->basename( qr{\.[^.]*$} );
	my $session = CGI->new();

	return ( $path, $pid, $session )
}

# @function - initialize
# @param - none
# @returns {array} - initial enviroment variables
sub pollenate
{
	# lets load the rest of the modules 
	require JSON;
	require File::Copy::Recursive;
	require Mustache::Simple;

	my ( $base ) = @_;
	my @paths = ( Path::Tiny::tempdir() );

	push @paths, $base->child($_) for ('vendor', 'templates', 'lib' ); 

	return @paths;
}


sub error
{
	my ($session, $message) = @_;
	croak $message;

	$session->header(-status => 404);
	exit(0);
}

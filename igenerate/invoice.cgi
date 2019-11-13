#!/usr/bin/env perl
use v5.12;
use strict;
use warnings;

use CGI qw(-utf8);
use CGI::Carp;
use Path::Tiny;
use Time::Piece;

use lib '.';
use cPanelUserConfig;

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

my ( $stache, $json, $build, $date, $phantomjs, $vendor, $template, $coffer ) = pollenate( $path->sibling( '.'.$pid ) );

$template = ( $session->param('tmpl') ) 
				? ennoble( $template, $session->param('tmpl') )
				: $template->child('default');

# lets copy contents of our template
File::Copy::Recursive::dircopy( $template, $build );

# lets calculate 
my $dataset = process( $json->decode( scalar $session->param('POSTDATA') ), $date );

# generate HTML
#----------------------------
$build->child('index.html')->spew( 
 	$stache->render( 
 		$build->child('index.html')->slurp,
 		$dataset
 	)
);

# Generate filename
#----------------------------
my $filename = generate( $dataset, $date );

# Generate PDF
#----------------------------
my @args = (
	# $vendor->child('phantomjs')->stringify,
	$phantomjs->stringify,
	$vendor->child('rasterize.js')->stringify,
	$build->child('index.html')->stringify,
	$path->sibling('download', $filename )->stringify
);

system(@args) == 0
        or croak "system @args failed: $?";

# JSON respond with link
#----------------------------
print $session->header('application/json');
print $json->encode( { 'status' => 200,'url' =>  join( '/', 'https:/', $ENV{'SERVER_NAME'}, 'download', $filename ) } );

exit(0);

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

# @function - pollenate
# @param - none
# @returns {array} - initial enviroment variables
sub pollenate
{
	# lets load the rest of the modules 
	require JSON;
	require File::Copy::Recursive;
	require Mustache::Simple;

	my $date = localtime;
	my ( $base ) = @_;
	my @enviro = ( Mustache::Simple->new(), JSON->new->utf8, Path::Tiny::tempdir(), $date, path('~/bin/phantomjs')->absolute );

	push @enviro, $base->child($_) for ( 'vendor', 'templates', 'coffer' ); 

	return @enviro;
}


# process - {description}
# @param - {...}
# @returns { .. }
# ----------------------------------------------------
sub process
{
	my ($data, $date) = @_;
	
	$data->{'subtotal'} = 0;
	
	foreach my $item ( @{$data->{'items'}} )
	{
		$item->{'cost'} = sprintf "%.2f", ($item->{'quantity'} * $item->{'price'});
		$data->{'subtotal'} += $item->{'cost'};
	}
	
	$data->{'subtotal'} = sprintf "%.2f", $data->{'subtotal'};
	# lets check to make sure we calculate tax
	unless ( $data->{'notax'} )
	{
		$data->{'tax'} = sprintf "%.2f", ($data->{'subtotal'} * 0.13 );
	}

	$data->{'total'} = sprintf "%.2f", ($data->{'subtotal'} + $data->{'tax'} );

	$data->{'timestamp'}->{'iso'} = $date->ymd;

	return $data;
}

# slugify - {description}
# @param - {...}
# @returns { .. }
# ----------------------------------------------------
sub slugify
{
	require Unicode::Normalize;

	my ($input) = @_;

    $input = Unicode::Normalize::NFKD($input);
    $input =~ tr/\000-\177//cd;    
    $input =~ s/[^\w\s-]//g;       
    $input =~ s/^\s+|\s+$//g;      
    $input = lc($input);
    $input =~ s/[-\s]+/-/g;        

    return $input;
}

sub generate
{
	my ( $data, $date ) = @_;
	return lc join( '.', slugify( $data->{'client'}->{'company'} ), $data->{'id'}, 'invoice.pdf')
}

# ennoble - {description}
# @param - {...}
# @returns { .. }
# ----------------------------------------------------
sub ennoble
{
	my ( $dir, $notation ) = @_;
	return $dir->child( split(/\./, $notation) );
}

# error - {description}
# @param - {...}
# @returns { .. }
# ----------------------------------------------------
sub error
{
	my ($session, $message) = @_;

	croak $message;

	$session->header(-status => 404);
	exit(0);
}


#!/usr/bin/env perl

use v5.12;
use warnings;

use Mustache::Simple;
use JSON qw/decode_json/;
use Path::Tiny qw/path cwd/;
use File::Copy::Recursive qw/fcopy dircopy/;

# ============================================
# PRE-INIT
# ============================================
my $base = path($0)->absolute;
my $current = cwd->absolute;
my $build = $base->parent()->sibling('.build');

# lets make sure there is a build
if ( ! $build->is_dir() )
{
	$build->mkpath();
}


my $config = {
	phantom => $base->sibling('phantomjs'),
	rasterize => $base->sibling('rasterize.js'),
	clients => $current->child('client'),
	invoices => $current->child('invoices')
};

my $stache = Mustache::Simple->new();


my $template = stage('invoice');

my $data = decode_json( $config->{clients}->child('block-media','2019-11.json')->slurp);

$build->child('index.html')->spew( $stache->render( $template->slurp, $data) );

sub stage
{
	my ( $template ) = $current->child( 'templates', shift );

	my $iter = $template->iterator;
	while ( my $path = $iter->() ) {
		if (! $path->is_dir() )
		{
			fcopy( $path->stringify, $build->stringify );
			next;
		}

		dircopy( $path->stringify, $build->child( $path->relative($template) ) );
	}

	return $build->child('index.html');
}


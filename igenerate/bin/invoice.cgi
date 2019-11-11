#!/usr/bin/env perl

use v5.12;
use warnings;

use Mustache::Simple;
use JSON qw/decode_json/;
use Path::Tiny qw/path cwd/;

# ============================================
# PRE-INIT
# ============================================
my $base = path($0)->absolute;
my $current = cwd->absolute;

# lets make sure there is a build
if ( ! $base->parent()->sibling('.build')->is_dir() )
{
	$base->parent()->sibling('.build')->mkpath();
}


my $config = {
	phantom => $base->sibling('phantomjs'),
	rasterize => $base->sibling('rasterize.js'),
	clients => $current->child('client')
	invoices => $current->child('invoices')
}

my $stache = Mustache::Simple->new();

say " BASE: ".$base->stringify." / CURRENT: $current";

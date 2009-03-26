#!/usr/bin/perl -I/home/hylom/local/lib/perl5
#
# FetchRSS.pl
# Fetch RSS & save content as text
# hylom, 2007
# hylomm@gmail.com
#
use strict;
use warnings;
use File::Touch;

# use UTF8 char code.
use utf8;
use open ":utf8";
use open ":std";

use LWP::Simple;
#use HTML::Parser;
#use File::Basename;
#use URI;
#use LWP::UserAgent;
use XML::RSS;
use DateTime::Format::W3CDTF;
use IO::File;

my $vers = '$Id: FetchRSS.pl,v 1.4 2008/12/16 17:37:38 hylom Exp $';

package FetchRSS;

my $save_dest = "/home/hylom/weblog/slashdot";
#my $save_dest = "/home/hylom/blog/entries";
#my $save_dest = "/home/hylom/weblog/slashdot";

my $THIS_PROG = "FetchRSS.pl";
my $USAGE = "usage: $THIS_PROG <URL>\n";

# get target URL
#my $target_url = shift @ARGV;
my $target_url = "http://slashdot.jp/~hylom/journal/rss";

my $target_html = LWP::Simple::get( $target_url );
utf8::decode($target_html);

print "FetchRSS.pl, $vers\n";

if( ! $target_html ) {
	die "Invaliid URL or error: $target_html.\n";
}

my $rss = new XML::RSS;
$rss->parse( $target_html );

my $item_list = $rss->{items};

my $num_updates = 0;
foreach my $item ( @{$item_list} ) {
	my $dt = DateTime::Format::W3CDTF->new
		->parse_datetime( $item->{dc}->{date} );

	my $output_file = "${save_dest}/" .  $dt->strftime("%Y%m%d-%H%M%S") . ".txt";
	my $output_fh = IO::File->new( $output_file, ">:utf8" );
	if( ! $output_fh ) {
		print "cannot open: $output_file.\n";
		next;
	}
#	foreach my $test ( keys %{$item->{dc}} ) {
#		print $test, "\n";
#	}
	print $output_fh $item->{title}, "\n";
#	print $output_fh $item->{dc}->{date}, "\n";
	print $output_fh $item->{content}->{encoded}, "\n";
#	print $output_fh $item->{description} "\n";
#	print $item{content:encoded}, "\n";

	$output_fh->close();

	File::Touch->new( mtime => $dt->epoch )->touch( $output_file );
	$num_updates++;
}

print "fetch $num_updates files: done.\n";
#print $target_html;


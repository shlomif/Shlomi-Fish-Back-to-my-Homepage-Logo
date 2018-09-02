#!/usr/bin/perl

use strict;
use warnings;

use XML::LibXML;

use Image::SVG::Path 'extract_path_info';

my $dom =
    XML::LibXML->load_xml(
    location => './back-to-my-homepage-slanted-path-union.svg' );
my $xpc = XML::LibXML::XPathContext->new($dom);
$xpc->registerNs( 'svg' => 'http://www.w3.org/2000/svg' );

my ($path_el) = $xpc->findnodes('//svg:path');

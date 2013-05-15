#!/usr/bin/perl

use strict;
use warnings;

use XML::LibXML;

my $dom = XML::LibXML->load_xml(
    location => './back-to-my-homepage-slanted-path-union.svg'
);
my $xpc = XML::LibXML::XPathContext->new($dom);
$xpc->registerNs('svg' => 'http://www.w3.org/2000/svg');

my ($node) = $xpc->findnodes('//svg:path');

print $node->toString(), "\n";

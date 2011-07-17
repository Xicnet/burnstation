#!/usr/bin/perl
# Script that changes file names to more user friendly ones 
# Copyright (C) 2006  Adam 'mulander' Wo³k
# e-mail netprobe@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
use warnings;
use strict;

use Getopt::Long;
use File::Find;

my %options;
Getopt::Long::Configure qw(bundling);
my $result = GetOptions( 	"help|h"	=> \$options{help},
				"version|V" 	=> \$options{version},
				"sub-space|S=s"	=> \$options{'sub-space'},
				"strip|s"	=> \$options{strip},
				"lower|l"	=> \$options{lower},
				"upper|u"	=> \$options{upper},
				"verbose|v+"	=> \$options{verbose},
				"dir-only|d"	=> \$options{'dir-only'},
				"file-only|f"	=> \$options{'file-only'},
				"force|F"	=> \$options{force},
				"trim|t=i"	=> \$options{trim});

##
# print out help message or version
if($options{help} || not defined @ARGV) { 
print<<EOF;
Usage: $0 options target

target		either a file or a directory

This script changes file names to more user friendly ones

Options:
-h, --help		display this help screen
-V, --version		display version information
-S, --sub-space=X	substitute spaces in the file name with a specified character
-s, --strip		remove all spaces from the file name
-l, --lower		transfer all upper case letters in the filename into lower case letters
-u, --upper		transfer all lower case letters in the filename into upper case letters
-v, --verbose		give verbose informations use multiple times to get even more verbose output
-d, --dir-only		only change directory names
-f, --file-only		only change file names
-F, --force		the script will change file names even if the destination name already exists
-t, --trim=X		trims the filename to given length ( must be more than 0 length )
EOF
exit;
} elsif($options{version}) {
print<<EOF;

fixname version 0.3

Script that changes file names to more user friendly ones 

Copyright (C) 2006 Adam 'mulander' Wo³k

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
EOF
exit;
}

###
# Start our work
my $counter = 0;

for my $target (@ARGV){
	finddepth(\&fixname,$target);
}
###
# print info
print "files renamed: $counter\n";
###
# fixname
sub fixname {
	my $target = $_;
	my $newname = $target;
	
	die "--sub-space and --strip shouldn't be used together\n"
		 if $options{'sub-space'} and $options{'strip'};
	die "--dir-only and --file-only shouldn't be used together\n"
		 if $options{'dir-only'} and $options{'file-only'};
	die "--lower and --upper shouldn't be used together\n"
		 if $options{lower} and $options{upper};
	return 0 if -f $target && $options{'dir-only'};
	return 0 if -d $target && $options{'file-only'};
		if(defined $options{'sub-space'}){
		$newname =~ s/\s/$options{'sub-space'}/g;
		}
		elsif(defined $options{strip}){
		$newname =~ s/\s//g;
		}
		if(defined $options{lower}){
		$newname = lc $newname;
		}
		elsif(defined $options{upper}){
		$newname = uc $newname;
		}
		if(defined $options{trim} && $options{trim} != 0){
			unless(length($newname) <= $options{trim}){
			my $suff = '';
			$suff 	 = $1 if s/\.(.+)$/./;
			$newname = substr $newname,0,($options{trim}-length($suff));
			$newname .= ".$suff" unless length($suff) == 0;
			}
		}
		if($newname ne $target) {
			if(!-e $newname || defined $options{force}) {
		print "renaming '$_' to '$newname'\n" 
						if defined $options{verbose} && $options{verbose} == 1;
		print "renaming '$File::Find::name' to '$newname'\n" 
						if defined $options{verbose} && $options{verbose} == 2;
		rename $target,$newname
				or warn "Can't rename file $target to $newname: $!\n";
		$counter++;
			} else {
		warn "'$newname' already exists, not renaming '$target'\n"
				if not defined $options{verbose};
		warn "'$newname' already exists in directory $File::Find::dir/, not renaming '$target'\n"
				if defined $options{verbose} && $options{verbose} >= 1;
			}
		
		}
	
}
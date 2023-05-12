# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from io import StringIO
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class PropertyRange:
    lower: int = -1
    upper: int = -1
    prop: str = None


@dataclass
class PropertyTable:
    lower_bounds: list[int] = field(default_factory=list)
    props_and_range: list[int] = field(default_factory=list)


LINE_REGEX = re.compile(
    r"^(?P<lower>[0-9A-F]{4,5})(?:\.\.(?P<upper>[0-9A-F]{4,5}))?\s*;\s*(?P<prop>\w+)")

def parse_property_line(inputLine: str) -> Optional[PropertyRange]:
    result = PropertyRange()
    if m := LINE_REGEX.match(inputLine):
        lower_str, upper_str, result.prop = m.group("lower", "upper", "prop")
        result.lower = int(lower_str, base=16)
        result.upper = result.lower
        if upper_str is not None:
            result.upper = int(upper_str, base=16)
        return result
    else:
        return None


def compact_property_ranges(input: list[PropertyRange]) -> list[PropertyRange]:
    """
    Merges consecutive ranges with the same property to one range.

    Merging the ranges results in fewer ranges in the output table,
    reducing binary size and improving lookup performance.
    """
    result = []
    for x in input:
        if (
            len(result)
            and result[-1].prop == x.prop
            and result[-1].upper + 1 == x.lower
        ):
            result[-1].upper = x.upper
            continue
        result.append(x)
    return result


PROP_VALUE_ENUMERATOR_TEMPLATE = "_{}_value"
PROP_VALUE_ENUM_TEMPLATE = """
{filename}
{timestamp}
enum class _{prop_name}_property_values : uint8_t {{
    {enumerators},
    _No_value = 255
}};
"""

DATA_ARRAY_TEMPLATE = """
{filename}
{timestamp}
inline constexpr _Unicode_property_data<_{prop_name}_property_values, {size}> _{prop_name}_property_data{{
    {{{lower_bounds}}},
    {{{props_and_size}}}
}};
"""

MSVC_FORMAT_UCD_TABLES_HPP_TEMPLATE = """
// __msvc_format_ucd_tables.hpp internal header

// Copyright (c) Microsoft Corporation.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

// WARNING, this entire header is generated by
// tools/unicode_properties_parse/grapheme_break_property_data_gen.py
// DO NOT MODIFY!

// UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE
//
// See Terms of Use <https://www.unicode.org/copyright.html>
// for definitions of Unicode Inc.'s Data Files and Software.
//
// NOTICE TO USER: Carefully read the following legal agreement.
// BY DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING UNICODE INC.'S
// DATA FILES ("DATA FILES"), AND/OR SOFTWARE ("SOFTWARE"),
// YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
// TERMS AND CONDITIONS OF THIS AGREEMENT.
// IF YOU DO NOT AGREE, DO NOT DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE
// THE DATA FILES OR SOFTWARE.
//
// COPYRIGHT AND PERMISSION NOTICE
//
// Copyright (c) 1991-2022 Unicode, Inc. All rights reserved.
// Distributed under the Terms of Use in https://www.unicode.org/copyright.html.
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of the Unicode data files and any associated documentation
// (the "Data Files") or Unicode software and any associated documentation
// (the "Software") to deal in the Data Files or Software
// without restriction, including without limitation the rights to use,
// copy, modify, merge, publish, distribute, and/or sell copies of
// the Data Files or Software, and to permit persons to whom the Data Files
// or Software are furnished to do so, provided that either
// (a) this copyright and permission notice appear with all copies
// of the Data Files or Software, or
// (b) this copyright and permission notice appear in associated
// Documentation.
//
// THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF
// ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
// WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT OF THIRD PARTY RIGHTS.
// IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS
// NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL
// DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
// DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
// TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
// PERFORMANCE OF THE DATA FILES OR SOFTWARE.
//
// Except as contained in this notice, the name of a copyright holder
// shall not be used in advertising or otherwise to promote the sale,
// use or other dealings in these Data Files or Software without prior
// written authorization of the copyright holder.

#pragma once
#ifndef __MSVC_FORMAT_UCD_TABLES_HPP
#define __MSVC_FORMAT_UCD_TABLES_HPP
#include <yvals_core.h>
#if _STL_COMPILER_PREPROCESSOR

#include <cstdint>
#include <limits>
#include <xutility>

#pragma pack(push, _CRT_PACKING)
#pragma warning(push, _STL_WARNING_LEVEL)
#pragma warning(disable : _STL_DISABLED_WARNINGS)
_STL_DISABLE_CLANG_WARNINGS
#pragma push_macro("new")
#undef new

_STD_BEGIN

template <class _ValueEnum, size_t _NumRanges>
struct _Unicode_property_data {{
    uint32_t _Lower_bounds[_NumRanges];
    uint16_t _Props_and_size[_NumRanges];
    _NODISCARD constexpr _ValueEnum _Get_property_for_codepoint(const uint32_t _Code_point) const noexcept {{
        ptrdiff_t _Upper_idx = _STD upper_bound(_Lower_bounds, _STD end(_Lower_bounds), _Code_point) - _Lower_bounds;
        constexpr auto _No_value_constant = static_cast<_ValueEnum>((numeric_limits<uint8_t>::max)());
        if (_Upper_idx == 0) {{
            return _No_value_constant;
        }}
        --_Upper_idx;
        const uint32_t _Lower_bound = _Lower_bounds[_Upper_idx];
        const uint16_t _Data        = _Props_and_size[_Upper_idx];
        const uint16_t _Size        = static_cast<uint16_t>(_Data & 0x0FFF);
        const _ValueEnum _Prop      = static_cast<_ValueEnum>((_Data & 0xF000) >> 12);
        _STL_INTERNAL_CHECK(_Code_point >= _Lower_bound);
        if (_Code_point < _Lower_bound + _Size) {{
            return _Prop;
        }}
        return _No_value_constant;
    }}
}};

// The following static data tables are generated from the Unicode character database.
// _Grapheme_Break_property_data comes from ucd/auxiliary/GraphemeBreakProperty.txt.
//
// _Extended_Pictographic_property_data comes from ucd/emoji/emoji-data.txt.
//
// The enums containing the values for the properties are also generated, in order to ensure they match
// up correctly with how we're parsing them.
//
// Both sets of data tables are generated by tools/unicode_properties_parse/grapheme_break_property_data_gen.py in the
// https://github.com/microsoft/stl repository.
//
// The data format is a set of arrays for each character property. The first is an array of uint32_t encoding
// the lower bound of each range of codepoints that has the given property.
// The second is an array of uint16_t encoding both the range size and property value as follows:
// 16               12                                   0
// +-----------------------------------------------------+
// | property_value  |              range_size           |
// +-----------------------------------------------------+
// that is: the size is stored in the least significant 12 bits
// (leading to a max size of 4095), and the property value is stored in the most significant 4 bits,
// leading to a maximum of 16 property values.
//
// Note that the Extended_Pictographic property only has one value, and we encode it as zero in the most significant 4
// bits, so the most significant 4 bits of _Props_and_size are "unused", in some sense.
//
// Codepoint ranges may not overlap, and, within one property, a codepoint may only appear once. Furthermore the
// codepoint lower bounds appear in sorted (ascending) order.

{content}
_STD_END

#pragma pop_macro("new")
_STL_RESTORE_CLANG_WARNINGS
#pragma warning(pop)
#pragma pack(pop)

#endif // _STL_COMPILER_PREPROCESSOR
#endif // __MSVC_FORMAT_UCD_TABLES_HPP
"""

def property_ranges_to_table(ranges: list[PropertyRange], props: list[str]) -> PropertyTable:
    result = PropertyTable()
    for range in sorted(ranges, key=lambda x: x.lower):
        result.lower_bounds.append(range.lower)
        size = (range.upper - range.lower) + 1
        assert size <= 0x0FFF
        prop_idx = props.index(range.prop)
        result.props_and_range.append(size | (prop_idx << 12))
    return result


def generate_cpp_data(filename: str, timestamp: str, prop_name: str, ranges: list[PropertyRange]) -> str:
    result = StringIO()
    prop_values = sorted({x.prop for x in ranges})
    table = property_ranges_to_table(ranges, prop_values)
    enumerator_values = [PROP_VALUE_ENUMERATOR_TEMPLATE.format(
        x) for x in prop_values]
    result.write(PROP_VALUE_ENUM_TEMPLATE.lstrip().format(
        filename=filename, timestamp=timestamp, prop_name=prop_name, enumerators=",".join(enumerator_values)))
    result.write("\n")
    result.write(DATA_ARRAY_TEMPLATE.lstrip().format(filename=filename, timestamp=timestamp, prop_name=prop_name,
                 size=len(table.lower_bounds),
                 lower_bounds=",".join(["0x" + format(x, 'x') for x in table.lower_bounds]),
                 props_and_size=",".join(["0x" + format(x, 'x') for x in table.props_and_range])))
    return result.getvalue()


def generate_data_tables() -> str:
    """
    Generate Unicode data for inclusion into <format> from
    GraphemeBreakProperty.txt and emoji-data.txt.

    GraphemeBreakProperty.txt can be found at
    https://www.unicode.org/Public/UCD/latest/ucd/auxiliary/GraphemeBreakProperty.txt

    emoji-data.txt can be found at
    https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt

    Both files are expected to be in the same directory as this script.
    """
    gbp_data_path = Path(__file__).absolute().with_name("GraphemeBreakProperty.txt")
    emoji_data_path = Path(__file__).absolute().with_name("emoji-data.txt")
    gbp_filename = ""
    gbp_timestamp = ""
    emoji_filename = ""
    emoji_timestamp = ""
    gbp_ranges = []
    emoji_ranges = []
    with gbp_data_path.open(encoding='utf-8') as f:
        gbp_filename = f.readline().replace("#", "//").rstrip()
        gbp_timestamp = f.readline().replace("#", "//").rstrip()
        gbp_ranges = compact_property_ranges([x for line in f if (x := parse_property_line(line))])
    with emoji_data_path.open(encoding='utf-8') as f:
        emoji_filename = f.readline().replace("#", "//").rstrip()
        emoji_timestamp = f.readline().replace("#", "//").rstrip()
        emoji_ranges = compact_property_ranges([x for line in f if (x := parse_property_line(line))])
    gpb_cpp_data = generate_cpp_data(gbp_filename, gbp_timestamp, "Grapheme_Break", gbp_ranges)
    emoji_cpp_data = generate_cpp_data(emoji_filename, emoji_timestamp, "Extended_Pictographic", [
        x for x in emoji_ranges if x.prop == "Extended_Pictographic"])
    return "\n".join([gpb_cpp_data, emoji_cpp_data])


if __name__ == "__main__":
    print(MSVC_FORMAT_UCD_TABLES_HPP_TEMPLATE.lstrip().format(content=generate_data_tables()))

/* Parser for INI Format configuration files.
 * All values are handled as Strings.
 * Handles comma-seperated array values.
 * Format Example:
 *
 * [Section]
 * Option = Value
 * Option = Value, Value, Value
 */
class INIParser {
  def structure = [:]

  /* INIParser Class Constructor
   * Arguments:
   *   iniString: INI Formatted String. Ie. from a `new File('path').getText()`
   */
  def INIParser(iniString) {
    parse(iniString);
  }

  /* Main INI Parsing Function. Parses INI String and converts to a Map Structure
   * Arguments:
   *   iniSource: INI Formatted String. See INIParser() Constructor.
   * Returns:
   *   The Resulting Map Structure of the iniSource String.
   */
  def parse(iniSource) {
    structure = [:];
    // Regex grabs Section in a group, then all the option, value pairs in a group
    iniSource.findAll(~/(?s)\[(.+?)\]\s*(.*?)\s*(?=\[|$)/) { match, section, items ->
      def items_structure = [:];
      // Regex grabs each option, value pair, parses arrays, and stores them
      items.findAll(~/(\S+)\s*=\s*(.+)\s*\n?/) { match2, key, item ->
        items_structure.put(key.trim(), (item.contains(','))? item.split(',')*.trim() : item.trim());
      }
      structure.put(section.trim(), items_structure);
    }
    return structure;
  }

  /* Get a list of Sections in the INI Strucutre.
   * Returns:
   *   List Object of all the INI Section Headers in the Map Structure.
   */
  def getSections() {
    return structure.keySet().toList();
  }

  /* Determine if a Section exists in the INI Structure
   * Arguments:
   *   section: String of section to determine the existance of.
   * Returns:
   *   True if section exists, false otherwise.
   */
  def hasSection(section) {
    return structure.containsKey(section);
  }

  /* Get a Map of all Option, Value pairs in a Section.
   * Arguments:
   *   section: The secret to return the Option Value pairs of.
   * Returns:
   *   Map of Option, Value pairs if section exists, else returns null.
   */
  def getSection(section) {
    return hasSection(section) ? structure[section] : null;
  }

  /* Get list of all Options available for a Section
   * Arguments:
   *   section: Section to return list of Options for.
   * Returns:
   *   List of Option Strings if section exists, else returns null.
   */
  def getOptions(section) {
    return hasSection(section) ? structure[section].keySet().toList() : null;
  }

  /* Determine if a Section exists in the INI Structure
   * Arguments:
   *   section: String of Section to determine the existance of.
   *   option: String of Option to determine the existance of.
   * Returns:
   *   True if section and option exists, false otherwise.
   */
  def hasOption(section, option) {
    return hasSection(section) ? structure[section].containsKey(option) : false;
  }

  /* Get list of all Values in an Option for a given Section
   * Arguments:
   *   section: Section to get Options from.
   *   option: Option to get Values from.
   * Returns:
   *   Value as String or List of String if section and option exists, else returns null.
   */
  def getOption(section, option) {
    return hasOption(section, item) ? structure[section][option] : null;
  }
}

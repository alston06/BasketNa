import React from "react";
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from "react-native";

interface Props {
  query: string;
  setQuery: (val: string) => void;
  onSearch: () => void;
}

export default function SearchBar({ query, setQuery, onSearch }: Props) {
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Enter product name..."
        value={query}
        onChangeText={setQuery}
      />
      <TouchableOpacity style={styles.searchBtn} onPress={onSearch}>
        <Text style={styles.searchBtnText}>Search</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: "center", marginVertical: 20 },
  searchInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    width: "90%",
    padding: 10,
    marginBottom: 10,
  },
  searchBtn: {
    backgroundColor: "#007BFF",
    padding: 12,
    borderRadius: 8,
    width: "90%",
    alignItems: "center",
  },
  searchBtnText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
});

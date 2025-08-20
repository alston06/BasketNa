import React, { useState } from "react";
import { SafeAreaView, View, Text, FlatList, StyleSheet } from "react-native";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import ResultCard from "../components/ResultCard";

export default function HomeScreen() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);

  const dummyData = [
    { id: "1", site: "Amazon", price: "₹999" },
    { id: "2", site: "Flipkart", price: "₹1,049" },
    { id: "3", site: "Myntra", price: "₹970" },
    { id: "4", site: "Snapdeal", price: "₹1,100" },
  ];

  const handleSearch = () => {
    if (query.trim() !== "") {
      setResults(dummyData);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Navbar />
      <SearchBar query={query} setQuery={setQuery} onSearch={handleSearch} />

      {results.length > 0 && (
        <View style={styles.results}>
          <Text style={styles.resultTitle}>Results for "{query}"</Text>
          <FlatList
            data={results}
            renderItem={({ item }) => <ResultCard item={item} />}
            keyExtractor={(item) => item.id}
          />
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  results: { marginTop: 20, paddingHorizontal: 10 },
  resultTitle: { fontSize: 18, fontWeight: "600", marginBottom: 10 },
});

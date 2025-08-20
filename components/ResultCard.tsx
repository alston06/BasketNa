import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface Props {
  item: { id: string; site: string; price: string };
}

export default function ResultCard({ item }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.site}>{item.site}</Text>
      <Text style={styles.price}>{item.price}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#f9f9f9",
    padding: 15,
    borderRadius: 10,
    marginVertical: 5,
    flexDirection: "row",
    justifyContent: "space-between",
    elevation: 2,
  },
  site: { fontSize: 16, fontWeight: "bold" },
  price: { fontSize: 16, color: "green", fontWeight: "bold" },
});

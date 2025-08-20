import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";

export default function Navbar() {
  return (
    <View style={styles.navbar}>
      <Text style={styles.logo}>PriceCheck</Text>
      <View style={styles.navButtons}>
        <TouchableOpacity style={styles.navBtn}>
          <Text style={styles.navBtnText}>Login</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navBtn}>
          <Text style={styles.navBtnText}>Signup</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  navbar: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
  },
  logo: { fontSize: 20, fontWeight: "bold", color: "#007BFF" },
  navButtons: { flexDirection: "row" },
  navBtn: { marginLeft: 15 },
  navBtnText: { fontSize: 16, color: "#007BFF" },
});

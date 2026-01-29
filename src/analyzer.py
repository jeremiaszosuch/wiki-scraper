from collections import Counter


class Analyzer:
    def convert_table_to_dicts(
        self,
        raw_table: list[list[str]],
        use_first_row_as_header: bool = False
    ) -> list[dict[str, str]]:
        if not raw_table:
            return []

        # Prepare data, if no header create dummy row
        processed_data = []
        if use_first_row_as_header:
            headers = raw_table[0]
            data_rows = raw_table[1:]
        else:
            num_columns = len(raw_table[0])
            headers = [f"Column_{i+1}" for i in range(num_columns)]
            data_rows = raw_table

        # Convert data into a dictionary
        for row in data_rows:
            if not row:
                continue
            processed_data.append(dict(zip(headers, row)))

        return processed_data

    def aggregate_word_counts(
        self,
        crawling_results: dict[str, dict[str, int]]
    ) -> dict[str, int]:
        # Aggregate word counts from all sites into one table
        global_counter = Counter()
        for page_data in crawling_results.values():
            global_counter.update(page_data)

        return dict(global_counter)

    def get_top_words(self, word_counts: dict[str, int], top_n: int = 10,
                      min_length: int = 0) -> list[tuple[str, int]]:
        filtered_items = []

        # Filter out words shorter than set length
        for word, count in word_counts.items():
            if len(word) < min_length:
                continue
            filtered_items.append((word, count))

        # Sort words in descending order
        sorted_items = sorted(filtered_items, key=lambda x: x[1], reverse=True)

        return sorted_items[:top_n]

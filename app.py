from hatano.core import Client
import streamlit as st
import io

# Streamlitアプリの設定
st.set_page_config(page_title="Excel Data Visualizer", layout="wide")
st.title("Excelデータの可視化ツール")

# アップロードウィジェット
uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx", "xls"])

if uploaded_file is not None:
    # 一時的なバッファにファイルを保存
    buffer = io.BytesIO(uploaded_file.getvalue())
    
    # Clientのインスタンスを作成
    client = Client(buffer)
    
    # 2カラムレイアウトの作成
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        # すべてのシートとその最初の行を表示
        st.subheader("利用可能なデータ")
        sheets_info = {}
        unique_chars = set()
        
        for sheet_name, df in client.sheets.items():
            if len(df.columns) > 0 and df.columns[0] == "ID":
                sheets_info[sheet_name] = df.head(1)
                if "Char" in df.columns:
                    # nanをスキップして有効な値のみを追加
                    valid_chars = df["Char"].dropna().astype(str).unique()
                    unique_chars.update(valid_chars)
        
        if sheets_info:
            st.write(f"{len(sheets_info)}つの有効なシートが見つかりました。")
            
            # 文字選択
            # クエリパラメータから初期値を取得
            default_char = st.query_params.get("char", None)
            if default_char and default_char in unique_chars:
                default_index = sorted(list(unique_chars)).index(default_char)
            else:
                default_index = 0

            selected_char = st.selectbox(
                "表示する文字を選択してください",
                options=sorted(list(unique_chars)),
                index=default_index
            )
            
            # 選択された文字をクエリパラメータに設定
            st.query_params["char"] = selected_char

            if selected_char:
                # 選択された文字のデータを抽出
                result_df = client.extract_char(selected_char)
                
                if not result_df.empty:
                    # データの一部を表示
                    st.subheader(f"'{selected_char}'のデータ")
                    st.dataframe(result_df)
                    
                    # 統計情報
                    st.subheader("統計情報")
                    st.write(result_df.describe())
                    
                    # 可視化を右カラムに表示
                    with right_col:
                        st.subheader("可視化")
                        fig = client.visualize(result_df)
                        st.pyplot(fig)
                else:
                    st.warning(f"'{selected_char}'に関するデータが見つかりませんでした。")
        else:
            st.error("有効なデータシートが見つかりませんでした。Excelファイルの形式を確認してください。")
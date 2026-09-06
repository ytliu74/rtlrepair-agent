module fifo (
    input  logic        clk,
    input  logic        reset,
    input  logic        wr_en,
    input  logic        rd_en,
    input  logic [7:0]  data_in,
    output logic [7:0]  data_out,
    output logic [4:0]  count,
    output logic        full,
    output logic        empty
);

    // 16-entry, 8-bit memory
    logic [7:0] mem [15:0];

    // 4-bit read and write pointers
    logic [3:0] rd_ptr, wr_ptr;

    // Accepted request wires
    logic        is_empty_q, is_full_q;
    logic        accept_read, accept_write;
    logic [4:0]  count_next;
    logic [3:0]  rd_ptr_next, wr_ptr_next;
    logic [7:0]  rd_data;

    // Evaluate occupancy before this rising edge
    assign is_empty_q = (count == 5'd0);
    assign is_full_q  = (count == 5'd16);

    // Read is accepted if FIFO not empty and rd_en
    assign accept_read  = rd_en && !is_empty_q;

    // Write is accepted if:
    // - Not full, or
    // - Full AND also read accepted this cycle (so it frees up space)
    assign accept_write = wr_en && (!is_full_q || accept_read);

    // Data read from old rd_ptr before next value
    assign rd_data = mem[rd_ptr];

    // Next wr_ptr and rd_ptr computation
    assign wr_ptr_next = accept_write  ? (wr_ptr + 4'd1) : wr_ptr;
    assign rd_ptr_next = accept_read   ? (rd_ptr + 4'd1) : rd_ptr;

    // Count next-state logic
    always_comb begin
        case ({accept_write, accept_read})
            2'b10: count_next = count + 5'd1;   // Write-only
            2'b01: count_next = count - 5'd1;   // Read-only
            2'b11: count_next = count;          // Simultaneous read/write
            default: count_next = count;        // No op
        endcase
    end

    // Main state/process
    always_ff @(posedge clk) begin
        if (reset) begin
            count     <= 5'd0;
            wr_ptr    <= 4'd0;
            rd_ptr    <= 4'd0;
            data_out  <= 8'd0;
        end else begin
            // Write
            if (accept_write)
                mem[wr_ptr] <= data_in;
            // Read
            if (accept_read)
                data_out <= rd_data;
            // No read accepted: data_out holds value
            
            // Update pointers
            wr_ptr  <= wr_ptr_next;
            rd_ptr  <= rd_ptr_next;

            // Update occupancy count
            count   <= count_next;

            // If read accepted but FIFO becomes empty (unlikely unless simultaneous write/read on last entry),
            // data_out holds last value. Otherwise, held.
        end
    end

    // Flag logic
    assign full  = (count == 5'd16);
    assign empty = (count == 5'd0);

endmodule

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

    // Storage for the FIFO entries
    logic [7:0] mem [0:15];
    // Pointers for reading and writing (4 bits for 16 entries)
    logic [3:0] rd_ptr, wr_ptr;

    // Accepted requests flags
    logic read_accept, write_accept;

    // Combinational flag for full and empty, next count
    always_comb begin
        full  = (count == 5'd16);
        empty = (count == 5'd0);

        // Determine request acceptance based on occupancy before edge
        read_accept  = rd_en & ~empty;
        write_accept = wr_en & (~full | read_accept);
    end

    // Sequential state update block
    always_ff @(posedge clk) begin
        if (reset) begin
            rd_ptr   <= 4'd0;
            wr_ptr   <= 4'd0;
            count    <= 5'd0;
            data_out <= 8'd0;
        end else begin
            // Data output update on accepted read
            if (read_accept) begin
                data_out <= mem[rd_ptr];
            end
            // Retain data_out if no accepted read (even if empty)

            // Write new data if accepted
            if (write_accept) begin
                mem[wr_ptr] <= data_in;
            end

            // Pointer and count logic
            unique case ({write_accept, read_accept})
                2'b00: begin
                    // Neither read nor write: no pointer change, no count change
                end
                2'b01: begin
                    // Read only
                    rd_ptr <= rd_ptr + 4'd1;
                    wr_ptr <= wr_ptr;
                    count  <= count - 5'd1;
                end
                2'b10: begin
                    // Write only
                    wr_ptr <= wr_ptr + 4'd1;
                    rd_ptr <= rd_ptr;
                    count  <= count + 5'd1;
                end
                2'b11: begin
                    // Simultaneous read and write; both pointers advance, count unchanged
                    rd_ptr <= rd_ptr + 4'd1;
                    wr_ptr <= wr_ptr + 4'd1;
                    count  <= count;
                end
            endcase
        end
    end

endmodule

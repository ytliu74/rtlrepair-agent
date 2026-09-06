// Hand-written infrastructure fixture, never substituted for model generation.
module fifo (
    input logic clk, reset, wr_en, rd_en,
    input logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic [4:0] count,
    output logic full, empty
);
    logic [7:0] memory [0:15];
    logic [3:0] head, tail;
    wire pop = rd_en && !empty;
    wire push = wr_en && (!full || pop);
    assign full = (count == 16);
    assign empty = (count == 0);
    always_ff @(posedge clk) begin
        if (reset) begin
            head <= 0;
            tail <= 0;
            count <= 0;
            data_out <= 0;
        end else begin
            if (pop) begin
                data_out <= memory[head];
                head <= head + 1'b1;
            end
            if (push) begin
                memory[tail] <= data_in;
                tail <= tail + 1'b1;
            end
            case ({push, pop})
                2'b10: count <= count + 1'b1;
                2'b01: count <= count - 1'b1;
                default: count <= count;
            endcase
        end
    end
endmodule

`timescale 1ns/1ps
module tb;
    reg clk = 0;
    reg reset = 0;
    reg enable = 0;
    wire [7:0] count;
    reg [7:0] expected = 0;
    integer checks = 0;
    integer i;
    counter dut(.clk(clk), .reset(reset), .enable(enable), .count(count));
    always #5 clk = ~clk;

    task check_count;
        input [7:0] wanted;
        begin
            checks = checks + 1;
            if (count !== wanted) begin
                $display("TEST_FAIL check=%0d expected=%0d got=%0d", checks, wanted, count);
                $fatal(1, "counter mismatch");
            end
        end
    endtask

    task step;
        input r;
        input e;
        begin
            @(negedge clk);
            #1;
            check_count(expected); // Reject falling-edge updates.
            reset = r;
            enable = e;
            #1;
            check_count(expected); // Reject asynchronous reset or combinational changes.
            @(posedge clk);
            if (r) expected = 0;
            else if (e) expected = expected + 8'd1;
            #1;
            check_count(expected); // Sample after nonblocking assignments settle.
        end
    endtask

    initial begin
        reset = 1;
        @(posedge clk);
        #1;
        check_count(0);
        step(0, 1);
        step(0, 1);
        step(0, 0);
        step(0, 0);
        step(1, 1); // Reset takes priority while count is nonzero.
        step(0, 1);
        step(1, 0); // Reset with enable low.
        for (i = 0; i < 260; i = i + 1) step(0, 1); // Includes 255 -> 0.
        for (i = 0; i < 16; i = i + 1) step(0, i % 3 != 0);
        step(0, 0);
        $display("Checks: %0d", checks);
        $display("TEST_PASS");
        $finish;
    end

    initial begin
        #10000;
        $display("TEST_FAIL watchdog timeout");
        $fatal(1, "timeout");
    end
endmodule

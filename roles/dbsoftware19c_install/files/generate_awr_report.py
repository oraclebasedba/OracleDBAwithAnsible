#!/usr/bin/env python3
"""
Oracle AWR Report Generator

This script connects to an Oracle database and generates an AWR report
for a specified time range.

Requirements:
- oracledb (formerly cx_Oracle) library
- Appropriate Oracle database privileges (SELECT on DBA_HIST_* views)
"""

import oracledb
import sys
from datetime import datetime, timedelta
import getpass


class AWRReportGenerator:
    def __init__(self, username, password, dsn):
        """
        Initialize the AWR Report Generator
        
        Args:
            username: Oracle database username
            password: Oracle database password
            dsn: Data Source Name (host:port/service_name)
        """
        self.username = username
        self.password = password
        self.dsn = dsn
        self.connection = None
        
    def connect(self):
        """Establish connection to Oracle database"""
        try:
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn
            )
            print(f"Successfully connected to Oracle database: {self.dsn}")
            return True
        except oracledb.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def get_database_id(self):
        """Get the database ID (DBID)"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT DBID FROM V$DATABASE")
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def get_instance_number(self):
        """Get the instance number"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT INSTANCE_NUMBER FROM V$INSTANCE")
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def get_snapshots(self, hours_back=2):
        """
        Get available snapshots from the last N hours
        
        Args:
            hours_back: Number of hours to look back for snapshots
            
        Returns:
            List of tuples (snap_id, begin_time, end_time)
        """
        cursor = self.connection.cursor()
        try:
            query = """
                SELECT SNAP_ID, 
                       BEGIN_INTERVAL_TIME, 
                       END_INTERVAL_TIME
                FROM DBA_HIST_SNAPSHOT
                WHERE BEGIN_INTERVAL_TIME >= SYSDATE - :hours/24
                ORDER BY SNAP_ID DESC
            """
            cursor.execute(query, hours=hours_back)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
    
    def list_recent_snapshots(self, count=10):
        """List the most recent snapshots"""
        cursor = self.connection.cursor()
        try:
            query = """
                SELECT SNAP_ID, 
                       TO_CHAR(BEGIN_INTERVAL_TIME, 'YYYY-MM-DD HH24:MI:SS') as BEGIN_TIME,
                       TO_CHAR(END_INTERVAL_TIME, 'YYYY-MM-DD HH24:MI:SS') as END_TIME
                FROM DBA_HIST_SNAPSHOT
                WHERE ROWNUM <= :count
                ORDER BY SNAP_ID DESC
            """
            cursor.execute(query, count=count)
            results = cursor.fetchall()
            
            print(f"\nMost recent {count} snapshots:")
            print("-" * 80)
            print(f"{'Snap ID':<10} {'Begin Time':<25} {'End Time':<25}")
            print("-" * 80)
            for snap_id, begin_time, end_time in results:
                print(f"{snap_id:<10} {begin_time:<25} {end_time:<25}")
            
            return results
        finally:
            cursor.close()
    
    def generate_awr_report_html(self, begin_snap_id, end_snap_id, output_file=None):
        """
        Generate AWR report in HTML format
        
        Args:
            begin_snap_id: Beginning snapshot ID
            end_snap_id: Ending snapshot ID
            output_file: Output file path (optional)
            
        Returns:
            AWR report content
        """
        cursor = self.connection.cursor()
        try:
            dbid = self.get_database_id()
            inst_num = self.get_instance_number()
            
            print(f"\nGenerating AWR report...")
            print(f"Database ID: {dbid}")
            print(f"Instance Number: {inst_num}")
            print(f"Begin Snapshot ID: {begin_snap_id}")
            print(f"End Snapshot ID: {end_snap_id}")
            
            # Use Oracle's built-in AWR report generation function
            query = """
                SELECT OUTPUT
                FROM TABLE(DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_HTML(
                    :dbid,
                    :inst_num,
                    :begin_snap,
                    :end_snap
                ))
            """
            
            cursor.execute(query, 
                          dbid=dbid, 
                          inst_num=inst_num, 
                          begin_snap=begin_snap_id, 
                          end_snap=end_snap_id)
            
            # Fetch all lines of the report
            report_lines = []
            for row in cursor:
                report_lines.append(row[0])
            
            report_content = '\n'.join(report_lines)
            
            # Save to file if output file is specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"\nAWR report saved to: {output_file}")
            
            return report_content
            
        except oracledb.Error as e:
            print(f"Error generating AWR report: {e}")
            return None
        finally:
            cursor.close()
    
    def generate_awr_report_text(self, begin_snap_id, end_snap_id, output_file=None):
        """
        Generate AWR report in text format
        
        Args:
            begin_snap_id: Beginning snapshot ID
            end_snap_id: Ending snapshot ID
            output_file: Output file path (optional)
            
        Returns:
            AWR report content
        """
        cursor = self.connection.cursor()
        try:
            dbid = self.get_database_id()
            inst_num = self.get_instance_number()
            
            # Use Oracle's built-in AWR report generation function for text
            query = """
                SELECT OUTPUT
                FROM TABLE(DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_TEXT(
                    :dbid,
                    :inst_num,
                    :begin_snap,
                    :end_snap
                ))
            """
            
            cursor.execute(query, 
                          dbid=dbid, 
                          inst_num=inst_num, 
                          begin_snap=begin_snap_id, 
                          end_snap=end_snap_id)
            
            # Fetch all lines of the report
            report_lines = []
            for row in cursor:
                report_lines.append(row[0])
            
            report_content = '\n'.join(report_lines)
            
            # Save to file if output file is specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"\nAWR report saved to: {output_file}")
            
            return report_content
            
        except oracledb.Error as e:
            print(f"Error generating AWR report: {e}")
            return None
        finally:
            cursor.close()


def main():
    """Main function to run the AWR report generator"""
    print("=" * 80)
    print("Oracle AWR Report Generator")
    print("=" * 80)
    
    # Get database connection details
    username = input("Enter Oracle username: ")
    password = getpass.getpass("Enter Oracle password: ")
    dsn = input("Enter DSN (host:port/service_name): ")
    
    # Create AWR generator instance
    awr_gen = AWRReportGenerator(username, password, dsn)
    
    # Connect to database
    if not awr_gen.connect():
        sys.exit(1)
    
    try:
        # List recent snapshots
        awr_gen.list_recent_snapshots(20)
        
        # Get snapshot IDs from user
        print("\n" + "=" * 80)
        begin_snap = input("Enter beginning snapshot ID: ")
        end_snap = input("Enter ending snapshot ID: ")
        
        # Validate input
        try:
            begin_snap_id = int(begin_snap)
            end_snap_id = int(end_snap)
        except ValueError:
            print("Error: Snapshot IDs must be integers")
            sys.exit(1)
        
        if begin_snap_id >= end_snap_id:
            print("Error: Beginning snapshot ID must be less than ending snapshot ID")
            sys.exit(1)
        
        # Choose report format
        print("\nReport format:")
        print("1. HTML")
        print("2. Text")
        format_choice = input("Choose format (1 or 2): ")
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice == "1":
            output_file = f"awr_report_{begin_snap_id}_{end_snap_id}_{timestamp}.html"
            awr_gen.generate_awr_report_html(begin_snap_id, end_snap_id, output_file)
        elif format_choice == "2":
            output_file = f"awr_report_{begin_snap_id}_{end_snap_id}_{timestamp}.txt"
            awr_gen.generate_awr_report_text(begin_snap_id, end_snap_id, output_file)
        else:
            print("Invalid format choice")
            sys.exit(1)
        
        print("\n" + "=" * 80)
        print("AWR report generation completed successfully!")
        print("=" * 80)
        
    finally:
        # Disconnect from database
        awr_gen.disconnect()


if __name__ == "__main__":
    main()
